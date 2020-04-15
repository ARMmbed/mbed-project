#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Objects representing Mbed program and library data."""
import logging

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# mbed program file names and constants.
TARGETS_JSON_FILE_PATH = Path("targets", "targets.json")
MBED_OS_DIR_NAME = "mbed-os"
MBED_OS_REFERENCE_URL = "https://github.com/ARMmbed/mbed-os"
MBED_OS_REFERENCE_FILE_NAME = "mbed-os.lib"
PROGRAM_ROOT_FILE_NAME = ".mbed"
APP_CONFIG_FILE_NAME = "mbed_app.json"


@dataclass
class GitReference:
    """Git reference for an Mbed library.

    Represents the contents of .lib file.

    Attributes:
        repo_url: URL of the library repository.
        ref: The commit sha, tag or branch.
    """

    repo_url: str
    ref: str


@dataclass
class MbedLibReference:
    """Metadata associated with an Mbed library.

    An Mbed library is an external dependency of an MbedProgram. The MbedProgram is made aware of the library
    dependency by the presence of a .lib file in the project tree, which we refer to as a library reference file. The
    library reference file contains a URI where the dependency's source code can be fetched.

    Attributes:
        reference_file: Path to the .lib reference file for this library.
        source_code_path: Path to the source code if it exists in the local project.
    """

    reference_file: Path
    source_code_path: Path

    def is_resolved(self) -> bool:
        """Determines if the source code for this library is present in the source tree."""
        return self.source_code_path.exists() and self.source_code_path.is_dir()

    def get_git_reference(self) -> GitReference:
        """Get the source code location from the library reference file.

        Returns:
            Data structure containing the contents of the library reference file.
        """
        raw_ref = self.reference_file.read_text().strip()
        url, sep, ref = raw_ref.partition("#")
        return GitReference(repo_url=url, ref=ref)


@dataclass
class MbedProgramData:
    """Metadata associated with an MbedProgram.

    This object holds paths to the various config files that can be found in an MbedProgram.

    Attributes:
        config_file: Path to mbed_app.json file. This can be `None` if the program doesn't set any custom config.
        mbed_file: Path to the .mbed file which defines the program root.
        mbed_os_ref: Library reference file for MbedOS. All programs require this file.
    """

    config_file: Optional[Path]
    mbed_file: Path
    mbed_os_ref: Path

    @classmethod
    def from_new(cls, root_path: Path) -> "MbedProgramData":
        """Create MbedProgramData from a new directory.

        A "new directory" in this context means it doesn't already contain an Mbed program.

        Args:
            root_path: The directory in which to create the program data files.

        Raises:
            ValueError: MbedProgramData already exists at this path.
        """
        config = root_path / APP_CONFIG_FILE_NAME
        mbed_file = root_path / PROGRAM_ROOT_FILE_NAME
        mbed_os_ref = root_path / MBED_OS_REFERENCE_FILE_NAME

        if mbed_file.exists() or mbed_os_ref.exists():
            raise ValueError(f"Program already exists at path {root_path}.")

        mbed_file.touch()
        config.touch()
        mbed_os_ref.write_text(MBED_OS_REFERENCE_URL)
        return cls(config_file=config, mbed_file=mbed_file, mbed_os_ref=mbed_os_ref)

    @classmethod
    def from_existing(cls, root_path: Path) -> "MbedProgramData":
        """Create MbedProgramData from a directory containing an existing program.

        Args:
            root_path: The path containing the MbedProgramData.

        Raises:
            ValueError: no MbedProgramData exists at this path.
        """
        config: Optional[Path]
        config = root_path / APP_CONFIG_FILE_NAME
        if not config.exists():
            logger.info("This program does not contain an mbed_app.json config file.")
            config = None

        mbed_os_file = root_path / MBED_OS_REFERENCE_FILE_NAME
        if not mbed_os_file.exists():
            raise ValueError("This path does not contain an mbed-os.lib, which is required for mbed programs.")

        mbed_file = root_path / PROGRAM_ROOT_FILE_NAME
        mbed_file.touch(exist_ok=True)

        return cls(config_file=config, mbed_file=mbed_file, mbed_os_ref=mbed_os_file)


@dataclass
class MbedOS:
    """Metadata associated with a copy of MbedOS.

    This object holds information about MbedOS used by MbedProgram.

    Attributes:
        root: The root path of the MbedOS source tree.
        targets_json_file: Path to a targets.json file, which contains target data specific to MbedOS revision.
    """

    root: Path
    targets_json_file: Path

    @classmethod
    def from_existing(cls, root_path: Path) -> "MbedOS":
        """Create MbedOS from a directory containing an existing MbedOS installation."""
        targets_json_file = root_path / TARGETS_JSON_FILE_PATH

        if not root_path.exists():
            raise ValueError("The mbed-os directory does not exist.")

        if not targets_json_file.exists():
            raise ValueError("This MbedOS copy does not contain a targets.json file.")

        return cls(root=root_path, targets_json_file=targets_json_file)

    @classmethod
    def from_new(cls, root_path: Path) -> "MbedOS":
        """Create MbedOS from an empty or new directory."""
        return cls(root=root_path, targets_json_file=root_path / TARGETS_JSON_FILE_PATH)

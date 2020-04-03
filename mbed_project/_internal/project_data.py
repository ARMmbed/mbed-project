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

    def get_git_reference(self) -> str:
        """Get the source code location from the library reference file.

        Returns:
            The contents of the library reference file as text.
        """
        return self.reference_file.read_text().strip()


@dataclass
class MbedProgramData:
    """Metadata associated with an MbedProgram.

    This object holds paths to the various config files that can be found in an MbedProgram.

    Attributes:
        config_file: Path to mbed_app.json file. This can be `None` if the program doesn't set any custom config.
        mbed_file: Path to the .mbed file which defines the program root.
    """

    config_file: Optional[Path]
    mbed_file: Path

    @classmethod
    def from_new(cls, root_path: Path) -> "MbedProgramData":
        """Create MbedProgramData from a new directory.

        A "new directory" in this context means it doesn't already contain an Mbed program.

        Args:
            root_path: The directory in which to create the program data files.

        Raises:
            ValueError: MbedProgramData already exists at this path.
        """
        config = root_path / "mbed_app.json"
        mbed_file = root_path / ".mbed"
        if mbed_file.exists():
            raise ValueError(f"Program already exists at path {root_path}.")

        mbed_file.touch()
        config.touch()
        return cls(config_file=config, mbed_file=mbed_file)

    @classmethod
    def from_existing(cls, root_path: Path) -> "MbedProgramData":
        """Create MbedProgramData from a directory containing an existing program.

        Args:
            root_path: The path containing the MbedProgramData.

        Raises:
            ValueError: no MbedProgramData exists at this path.
        """
        config: Optional[Path]
        config = root_path / "mbed_app.json"
        if not config.exists():
            logger.info("This program does not contain an mbed_app.json config file.")
            config = None

        mbed_file = root_path / ".mbed"
        if not mbed_file.exists():
            raise ValueError(f"An Mbed program does not exist at {root_path}")

        return cls(config_file=config, mbed_file=mbed_file)


@dataclass
class MbedOS:
    """Metadata associated with a copy of MbedOS.

    This object holds information about MbedOS used by MbedProgram.

    Attributes:
        targets_json_file: Path to a targets.json file, which contains target data specific to MbedOS revision.
    """

    targets_json_file: Path

    @classmethod
    def from_existing(cls, root_path: Path) -> "MbedOS":
        """Create MbedOS from a directory constaining an existing MbedOS installation."""
        targets_json_file = root_path / "targets" / "targets.json"

        if not targets_json_file.exists():
            raise ValueError("This MbedOS copy does not contain a targets.json file.")
        return cls(targets_json_file=targets_json_file)

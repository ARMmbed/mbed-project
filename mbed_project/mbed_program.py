#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Mbed Program abstraction layer."""
import logging

from pathlib import Path
from typing import Optional

import git

from mbed_project.exceptions import VersionControlError, ProgramNotFound, ExistingProgram
from mbed_project._internal.project_data import MbedProgramData, MbedOS

logger = logging.getLogger(__name__)


class MbedProgram:
    """Represents an Mbed program.

    An `MbedProgram` consists of a git repo and `MbedProgramData`. The `MbedProgramData` contains configuration files
    used for building an Mbed application, and a .mbed file which defines the program's root path.

    `MbedProgram` provides classmethods to cope with different initialisation scenarios.
    """

    def __init__(self, repo: git.Repo, program_data: MbedProgramData, mbed_os: Optional[MbedOS]) -> None:
        """Initialise the program attributes.

        Args:
            repo: The program's associated git repository.
            program_data: An instance of `MbedProgramData` containing metadata about the program.
            mbed_os: An instance of `MbedOS` containing metadata about the Mbed OS copy used.
        """
        self.repo = repo
        self.metadata = program_data
        self.mbed_os = mbed_os

    @classmethod
    def from_remote_url(cls, url: str, dst_path: Path) -> "MbedProgram":
        """Fetch an Mbed program from a remote URL.

        Args:
            url: URL of the remote program repository.
            dst_path: Destination path for the cloned program.

        Raises:
            ExistingProgram: `dst_path` already contains an Mbed program.
        """
        if _tree_contains_program(dst_path):
            raise ExistingProgram(
                f"The destination path '{dst_path}' already contains an Mbed program. Please set the destination path "
                "to an empty directory."
            )

        logger.info(f"Cloning Mbed program from URL {url}")
        try:
            repo = git.Repo.clone_from(url, str(dst_path))
        except git.exc.GitCommandError as e:
            raise VersionControlError(f"Failed to clone from the remote URL. Error from VCS: {e.stderr}.")

        program = MbedProgramData.from_existing(dst_path)
        mbed_os = None
        return cls(repo, program, mbed_os)

    @classmethod
    def from_new_local_directory(cls, dir_path: Path) -> "MbedProgram":
        """Create an MbedProgram from an empty directory.

        Creates the directory if it doesn't exist.

        Args:
            dir_path: Directory in which to create the program.

        Raises:
            ExistingProgram: An existing program was found in the path.
        """
        if _tree_contains_program(dir_path):
            raise ExistingProgram(
                f"An existing Mbed program was found in the directory tree {dir_path}. It is not possible to nest Mbed "
                "programs. Please ensure there is no .mbed file in the cwd hierarchy."
            )

        logger.info(f"Creating Mbed program at path {dir_path.resolve()}")
        dir_path.mkdir(exist_ok=True)
        program_data = MbedProgramData.from_new(dir_path)
        logger.info(f"Creating git repository for the Mbed program {dir_path}")
        repo = git.Repo.init(str(dir_path))
        mbed_os = None
        return cls(repo, program_data, mbed_os)

    @classmethod
    def from_existing_local_program_directory(cls, dir_path: Path) -> "MbedProgram":
        """Create an MbedProgram from an existing program directory.

        Args:
            dir_path: Directory containing an Mbed program.

        Raises:
            ProgramNotFound: An existing program was not found in the path.
        """
        program_root = _find_program_root(dir_path)
        logger.info(f"Found existing Mbed program at path '{program_root}'")
        repo = git.Repo(str(program_root))
        program = MbedProgramData.from_existing(program_root)
        mbed_os = MbedOS.from_existing(program_root / "mbed-os")
        return cls(repo, program, mbed_os)


def _tree_contains_program(path: Path) -> bool:
    """Check if the current path or its ancestors contain a .mbed file.

    Args:
        path: The starting path for the search. The search walks up the tree from this path.

    Returns:
        `True` if a .mbed file is located between `path` and filesystem root.
        `False` if no .mbed file was found.
    """
    try:
        _find_program_root(path)
        return True
    except ProgramNotFound:
        return False


def _find_program_root(cwd: Path) -> Path:
    """Walk up the directory tree, looking for a .mbed file.

    Programs contain a .mbed file at the root of the source tree.

    Args:
        cwd: The directory path to search for a program.

    Returns:
        Path containing the .mbed file.
    """
    potential_root = cwd.resolve()
    while str(potential_root) != str(potential_root.root):
        logging.debug(f"Searching for .mbed file at path {potential_root}")
        if (potential_root / ".mbed").exists():
            return potential_root
        potential_root = potential_root.parent

    raise ProgramNotFound(
        f"No program found from {cwd.resolve()} to {cwd.resolve().root}. Please set the cwd to a program directory or "
        "subdirectory."
    )

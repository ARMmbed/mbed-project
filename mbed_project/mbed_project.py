#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Defines the public API of the package."""
import pathlib

from typing import List

from mbed_project.mbed_program import MbedProgram


def clone_project(url: str, recursive: bool = False) -> None:
    """Clones an Mbed project from a remote repository.

    Args:
        url: URL of the repository to clone.
        recursive: Recursively clone all project dependencies.
    """
    pass


def initialise_project(path: pathlib.Path, create_only: bool) -> None:
    """Create a new Mbed project, optionally fetching and adding mbed-os.

    Args:
        path: Path to the project folder. Created if it doesn't exist.
        create_only: Flag which suppreses fetching mbed-os. If the value is `False`, fetch mbed-os from the remote.
    """
    program = MbedProgram.from_new_local_directory(path)
    if not create_only:
        program.resolve_libraries()


def checkout_project_revision(path: pathlib.Path, project_revision: str, force: bool = False) -> None:
    """Checkout a specific revision of the current Mbed project.

    This function also resolves and syncs all library dependencies to the revision specified in the library reference
    files.

    Args:
        path: Path to the Mbed project.
        project_revision: Revision of the Mbed project to check out.
        force: Force overwrite uncommitted changes. If False, the checkout will fail if there are uncommitted local
               changes.
    """
    pass


def get_libs(path: pathlib.Path) -> List[str]:
    """List all resolved library dependencies.

    This function will not resolve dependencies. This will only generate a list of resolved dependencies.

    Args:
        path: Path to the Mbed project.
    """
    return [""]

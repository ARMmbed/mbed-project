#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Entry point for mbed-tools cli."""
import os
import pathlib

import click

from mbed_project import initialise_project, clone_project, get_libs, checkout_project_revision


@click.command()
@click.option(
    "--fetch-mbed-os",
    "-m",
    is_flag=True,
    show_default=True,
    help="Fetch mbed-os from online repository and add it to the project.",
)
@click.argument("path", type=click.Path())
def init(path: str, fetch_mbed_os: bool) -> None:
    """Creates a new Mbed project at the specified path. Optionally downloading mbed-os and adding it to the project.

    PATH: Path to the destination directory for the project. Will be created if it does not exist.
    """
    initialise_project(pathlib.Path(path), fetch_mbed_os)


@click.command()
@click.argument("url")
def clone(url: str) -> None:
    """Clone an Mbed project and library dependencies.

    URL: The git url of the remote project to clone.
    """
    clone_project(url)


@click.command()
@click.argument("path", type=click.Path(), default=os.getcwd())
def libs(path: str) -> None:
    """List all resolved library dependencies.

    PATH: Path to the Mbed project [default: CWD]
    """
    get_libs(pathlib.Path(path))


@click.command()
@click.argument("path", type=click.Path(), default=os.getcwd())
@click.argument("revision", default="latest")
@click.option(
    "--force", "-f", is_flag=True, show_default=True, help="Force checkout, overwrites local uncommitted changes."
)
def checkout(path: str, revision: str, force: bool) -> None:
    """Checks out an Mbed project at the specified revision.

    Ensures all dependencies are resolved and the versions are synchronised to the version specified in the library
    reference.

    PATH: Path to the Mbed project [default: CWD]

    REVISION: The revision of the Mbed project to check out.
    """
    checkout_project_revision(pathlib.Path(path), revision, force)

#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Entry point for mbed-tools cli."""
import os
import pathlib

import click

from mbed_project import initialise_project, clone_project, list_libs, checkout_project_revision


@click.command()
@click.option("--create-only", "-c", is_flag=True, show_default=True, help="Create a program without fetching mbed-os.")
@click.argument("path", type=click.Path())
def init(path: str, create_only: bool) -> None:
    """Creates a new Mbed project at the specified path. Downloads mbed-os and adds it to the project.

    PATH: Path to the destination directory for the project. Will be created if it does not exist.
    """
    click.echo(f"Creating a new Mbed program at path '{path}'.")
    if not create_only:
        click.echo("Downloading mbed-os and adding it to the project.")

    initialise_project(pathlib.Path(path), create_only)


@click.command()
@click.argument("url")
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    show_default=True,
    help="Resolve all library dependencies after cloning the program..",
)
def clone(url: str, recursive: bool) -> None:
    """Clone an Mbed project and library dependencies.

    URL: The git url of the remote project to clone.
    """
    click.echo(f"Cloning Mbed program '{url}'")
    if recursive:
        click.echo("Resolving program library dependencies.")

    clone_project(url, recursive)


@click.command()
@click.argument("path", type=click.Path(), default=os.getcwd())
def libs(path: str) -> None:
    """List all resolved library dependencies.

    PATH: Path to the Mbed project [default: CWD]
    """
    lib_data = list_libs(pathlib.Path(path))
    click.echo("This program has the following library dependencies: ")
    click.echo("\n".join(sorted(lib_data["known_libs"])))
    if lib_data["unresolved"]:
        click.echo("Unresolved libraries detected. Please run the `checkout` command to download library source code.")


@click.command()
@click.argument("path", type=click.Path(), default=os.getcwd())
@click.option(
    "--force", "-f", is_flag=True, show_default=True, help="Force checkout, overwrites local uncommitted changes."
)
def checkout(path: str, force: bool) -> None:
    """Checks out an Mbed project at the specified revision.

    Ensures all dependencies are resolved and the versions are synchronised to the version specified in the library
    reference.

    PATH: Path to the Mbed project [default: CWD]

    REVISION: The revision of the Mbed project to check out.
    """
    click.echo("Checking out all libraries to revisions specified in .lib files. Resolving any unresolved libraries.")
    checkout_project_revision(pathlib.Path(path), force)


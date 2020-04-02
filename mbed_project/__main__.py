#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Entrypoint for development purposes."""
import click

from mbed_project.mbed_tools import init, checkout, libs, clone


@click.group()
def group() -> None:
    """Groups commands."""
    pass


group.add_command(init)
group.add_command(clone)
group.add_command(libs)
group.add_command(checkout)
group()

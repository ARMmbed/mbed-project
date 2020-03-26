#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Entry point for mbed-tools cli."""
import click


@click.command()
def cli():
    """Prints Hello."""
    click.echo("Hello.")

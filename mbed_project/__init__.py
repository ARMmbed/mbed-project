#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Exposes the primary interfaces for the library."""

from mbed_project._version import __version__
from mbed_project.mbed_project import initialise_project, clone_project, checkout_project_revision, get_libs
from mbed_project.mbed_program import MbedProgram

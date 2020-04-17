#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib

from unittest import TestCase, mock

from mbed_project import initialise_project


@mock.patch("mbed_project.mbed_project.MbedProgram", autospec=True)
class TestInitialiseProject(TestCase):
    def test_fetches_mbed_os_when_create_only_is_false(self, mock_program):
        path = pathlib.Path()
        initialise_project(path, create_only=False)

        mock_program.from_new_local_directory.assert_called_once_with(path)
        mock_program.from_new_local_directory.return_value.resolve_libraries.assert_called_once()

    def test_skips_mbed_os_when_create_only_is_true(self, mock_program):
        path = pathlib.Path()
        initialise_project(path, create_only=True)

        mock_program.from_new_local_directory.assert_called_once_with(path)
        mock_program.from_new_local_directory.return_value.resolve_libraries.assert_not_called()

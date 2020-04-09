#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib

from unittest import TestCase, mock

from click.testing import CliRunner

from mbed_project.mbed_tools import init, clone, checkout, libs


@mock.patch("mbed_project.mbed_tools.cli.initialise_project", autospec=True)
class TestInitCommand(TestCase):
    def test_calls_init_function_with_correct_args(self, mock_initialise_project):
        CliRunner().invoke(init, ["path", "--create-only"])
        mock_initialise_project.assert_called_once_with(pathlib.Path("path"), True)


@mock.patch("mbed_project.mbed_tools.cli.clone_project", autospec=True)
class TestCloneCommand(TestCase):
    def test_calls_clone_function_with_correct_args(self, mocked_clone_project):
        CliRunner().invoke(clone, ["url"])
        mocked_clone_project.assert_called_once_with("url")


@mock.patch("mbed_project.mbed_tools.cli.get_libs", autospec=True)
class TestLibsCommand(TestCase):
    def test_calls_libs_function(self, mocked_get_libs):
        CliRunner().invoke(libs)
        mocked_get_libs.assert_called_once()


@mock.patch("mbed_project.mbed_tools.cli.checkout_project_revision", autospec=True)
class TestCheckoutCommand(TestCase):
    def test_calls_checkout_function_with_correct_args(self, mocked_checkout_project_revision):
        CliRunner().invoke(checkout, ["path", "revision", "--force"])
        mocked_checkout_project_revision.assert_called_once_with(pathlib.Path("path"), "revision", True)

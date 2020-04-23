#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from pathlib import Path
from unittest import TestCase, mock

from mbed_project.exceptions import VersionControlError
from mbed_project._internal import git_utils


class TestClone(TestCase):
    @mock.patch("mbed_project._internal.git_utils.git.Repo", autospec=True)
    @mock.patch("mbed_project._internal.git_utils.ProgressReporter", autospec=True)
    def test_returns_repo(self, mock_progress, mock_repo):
        url = "https://blah"
        path = Path()
        repo = git_utils.clone(url, path)

        self.assertIsNotNone(repo)
        mock_repo.clone_from.assert_called_once_with(url, str(path), progress=mock_progress())

    def test_raises_when_clone_fails(self):
        with self.assertRaises(VersionControlError):
            git_utils.clone("", Path())


@mock.patch("mbed_project._internal.git_utils.git.Repo", autospec=True)
class TestInit(TestCase):
    def test_returns_initialised_repo(self, mock_repo):
        repo = git_utils.init(Path())

        self.assertIsNotNone(repo)
        mock_repo.init.assert_called_once_with(str(Path()))

    def test_raises_when_init_fails(self, mock_repo):
        mock_repo.init.side_effect = git_utils.git.exc.GitCommandError("git init", 255)

        with self.assertRaises(VersionControlError):
            git_utils.init(Path())

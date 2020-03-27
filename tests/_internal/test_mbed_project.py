#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib

from unittest import mock, TestCase

import git

from pyfakefs.fake_filesystem_unittest import patchfs

from mbed_project._internal.program import MbedProgram, _find_program_root
from mbed_project._internal.program import ExistingProgram, ProgramNotFound, VersionControlError
from tests.factories import make_mbed_program_files


class TestInitialiseProgram(TestCase):
    @patchfs
    def test_from_new_local_dir_raises_if_path_is_existing_program(self, fs):
        program_root = pathlib.Path("programfoo")
        fs.create_file(str(program_root / ".mbed"))

        with self.assertRaises(ExistingProgram):
            MbedProgram.from_new_local_directory(program_root)

    @patchfs
    @mock.patch("mbed_project._internal.program.git.Repo", autospec=True)
    def test_from_new_local_dir_generates_valid_program(self, mock_repo, fs):
        fs_root = pathlib.Path("foo")
        fs.create_dir(str(fs_root))
        program_root = fs_root / "programfoo"

        program = MbedProgram.from_new_local_directory(program_root)

        self.assertTrue(program.metadata.mbed_file.exists())
        mock_repo.init.assert_called_once_with(str(program_root))

    @patchfs
    @mock.patch("mbed_project._internal.program.git.Repo", autospec=True)
    def test_from_url_raises_if_clone_fails(self, mock_repo, fs):
        fs_root = pathlib.Path("foo")
        fs.create_dir(str(fs_root))
        url = "https://notvalid.com"
        mock_repo.clone_from.side_effect = git.exc.GitCommandError("git clone", 127)

        with self.assertRaises(VersionControlError):
            MbedProgram.from_remote_url(url, fs_root)

    @patchfs
    def test_from_url_raises_if_dest_dir_contains_program(self, fs):
        fs_root = pathlib.Path("foo")
        make_mbed_program_files(fs_root, fs)
        url = "https://valid"

        with self.assertRaises(ExistingProgram):
            MbedProgram.from_remote_url(url, fs_root)

    @patchfs
    @mock.patch("mbed_project._internal.program._tree_contains_program", autospec=True)
    @mock.patch("mbed_project._internal.program.git.Repo", autospec=True)
    def test_from_url_returns_valid_program(self, mock_repo, mock_tree_contains_program, fs):
        fs_root = pathlib.Path("foo")
        make_mbed_program_files(fs_root, fs)
        url = "https://valid"
        mock_tree_contains_program.return_value = False

        program = MbedProgram.from_remote_url(url, fs_root)

        self.assertTrue(program.metadata.mbed_file.exists())
        mock_repo.clone_from.assert_called_once_with(url, str(fs_root))

    @patchfs
    def test_from_existing_raises_if_path_is_not_a_program(self, fs):
        fs_root = pathlib.Path("foo")
        fs.create_dir(str(fs_root))
        program_root = fs_root / "programfoo"

        with self.assertRaises(ProgramNotFound):
            MbedProgram.from_existing_local_program_directory(program_root)

    @patchfs
    @mock.patch("mbed_project._internal.program.git.Repo", autospec=True)
    def test_from_existing_returns_valid_program(self, mock_repo, fs):
        fs_root = pathlib.Path("/foo")
        make_mbed_program_files(fs_root, fs)

        program = MbedProgram.from_existing_local_program_directory(fs_root)

        self.assertTrue(program.metadata.mbed_file.exists())
        mock_repo.assert_called_once_with(str(fs_root))


class TestFindProgramRoot(TestCase):
    @patchfs
    def test_finds_program_higher_in_dir_tree(self, fs):
        fs_root = pathlib.Path("foo")
        pwd = fs_root / "subprojfoo" / "libbar"
        make_mbed_program_files(fs_root, fs)
        fs.create_dir(str(pwd))

        self.assertTrue(_find_program_root(pwd))

    @patchfs
    def test_finds_program_at_current_path(self, fs):
        fs_root = pathlib.Path("foo")
        make_mbed_program_files(fs_root, fs)

        self.assertTrue(_find_program_root(fs_root))

    @patchfs
    def test_raises_if_no_program_found(self, fs):
        fs_root = pathlib.Path("foo")
        fs.create_dir(str(fs_root))

        with self.assertRaises(ProgramNotFound):
            _find_program_root(fs_root)

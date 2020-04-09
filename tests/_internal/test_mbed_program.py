#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib

from unittest import mock, TestCase

import git

from pyfakefs.fake_filesystem_unittest import patchfs

from mbed_project import MbedProgram
from mbed_project.exceptions import ExistingProgram, ProgramNotFound, VersionControlError
from mbed_project.mbed_program import _find_program_root
from mbed_project._internal.project_data import MbedProgramData, MbedLibReference, MbedOS
from tests.factories import make_mbed_program_files, make_mbed_lib_reference, make_mbed_os_files


class TestInitialiseProgram(TestCase):
    @patchfs
    def test_from_new_local_dir_raises_if_path_is_existing_program(self, fs):
        program_root = pathlib.Path("programfoo")
        fs.create_file(str(program_root / ".mbed"))

        with self.assertRaises(ExistingProgram):
            MbedProgram.from_new_local_directory(program_root)

    @patchfs
    @mock.patch("mbed_project.mbed_program.git.Repo", autospec=True)
    def test_from_new_local_dir_generates_valid_program(self, mock_repo, fs):
        fs_root = pathlib.Path("foo")
        fs.create_dir(str(fs_root))
        program_root = fs_root / "programfoo"

        program = MbedProgram.from_new_local_directory(program_root)

        self.assertEqual(program.metadata, MbedProgramData.from_existing(program_root))
        self.assertEqual(program.repo, mock_repo.init.return_value)
        mock_repo.init.assert_called_once_with(str(program_root))

    @patchfs
    @mock.patch("mbed_project.mbed_program.git.Repo", autospec=True)
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
    @mock.patch("mbed_project.mbed_program.git.Repo", autospec=True)
    def test_from_url_raises_if_cloned_repo_is_not_program(self, mock_repo, fs):
        fs_root = pathlib.Path("foo")
        fs.create_dir(str(fs_root))
        url = "https://validrepo.com"
        mock_repo.clone_from.side_effect = lambda url, dst_dir: fs.create_dir(dst_dir)

        with self.assertRaises(ProgramNotFound):
            MbedProgram.from_remote_url(url, fs_root / "corrupt-prog")

    @patchfs
    @mock.patch("mbed_project.mbed_program._tree_contains_program", autospec=True)
    @mock.patch("mbed_project.mbed_program.git.Repo", autospec=True)
    def test_from_url_returns_valid_program(self, mock_repo, mock_tree_contains_program, fs):
        fs_root = pathlib.Path("foo")
        make_mbed_program_files(fs_root, fs)
        url = "https://valid"
        mock_tree_contains_program.return_value = False

        program = MbedProgram.from_remote_url(url, fs_root)

        self.assertEqual(program.metadata, MbedProgramData.from_existing(fs_root))
        self.assertEqual(program.repo, mock_repo.clone_from.return_value)
        mock_repo.clone_from.assert_called_once_with(url, str(fs_root))

    @patchfs
    def test_from_existing_raises_if_path_is_not_a_program(self, fs):
        fs_root = pathlib.Path("foo")
        fs.create_dir(str(fs_root))
        program_root = fs_root / "programfoo"

        with self.assertRaises(ProgramNotFound):
            MbedProgram.from_existing_local_program_directory(program_root)

    @patchfs
    @mock.patch("mbed_project.mbed_program.git.Repo", autospec=True)
    def test_from_existing_returns_valid_program(self, mock_repo, fs):
        fs_root = pathlib.Path("/foo")
        make_mbed_program_files(fs_root, fs)
        make_mbed_os_files(fs_root / "mbed-os", fs)

        program = MbedProgram.from_existing_local_program_directory(fs_root)

        self.assertEqual(program.metadata, MbedProgramData.from_existing(fs_root))
        self.assertEqual(program.mbed_os, MbedOS.from_existing(fs_root / "mbed-os"))
        self.assertEqual(program.repo, mock_repo.return_value)
        mock_repo.assert_called_once_with(str(fs_root))


@mock.patch("mbed_project.mbed_program.git.Repo", autospec=True)
class TestMbedProgramLibraryHandling(TestCase):
    @patchfs
    @mock.patch("mbed_project.mbed_program.ProgressReporter")
    def test_hydrates_top_level_library_references(self, progress_mock, mock_repo, fs):
        fs_root = pathlib.Path("/foo")
        make_mbed_program_files(fs_root, fs)
        make_mbed_os_files(fs_root / "mbed-os", fs)
        lib = make_mbed_lib_reference(fs_root, fs, ref_url="https://git")
        mock_repo.clone_from.side_effect = lambda url, dst_dir, progress: fs.create_dir(dst_dir)

        program = MbedProgram.from_existing_local_program_directory(fs_root)
        program.resolve_libraries()

        mock_repo.clone_from.assert_called_once_with(
            lib.get_git_reference().repo_url, str(lib.source_code_path), progress=progress_mock()
        )
        self.assertTrue(lib.is_resolved())

    @patchfs
    def test_hydrates_recursive_dependencies(self, mock_repo, fs):
        fs_root = pathlib.Path("/foo")
        make_mbed_program_files(fs_root, fs)
        make_mbed_os_files(fs_root / "mbed-os", fs)
        lib = make_mbed_lib_reference(fs_root, fs, ref_url="https://git")
        # Create a lib reference without touching the fs at this point, we want to mock the effects of a recursive
        # reference lookup and we need to assert the reference was resolved.
        lib2 = MbedLibReference(
            reference_file=(lib.source_code_path / "lib2.lib"), source_code_path=(lib.source_code_path / "lib2")
        )
        # Here we mock the effects of a recursive reference lookup. We create a new lib reference as a side effect of
        # the first call to the mock. Then we create the src dir, thus resolving the lib, on the second call.
        mock_repo.clone_from.side_effect = lambda url, dst_dir, progress: (
            make_mbed_lib_reference(pathlib.Path(dst_dir), fs, name=lib2.reference_file.name, ref_url="https://valid2"),
            fs.create_dir(lib2.source_code_path),
        )

        program = MbedProgram.from_existing_local_program_directory(fs_root)
        program.resolve_libraries()

        self.assertTrue(lib.is_resolved())
        self.assertTrue(lib2.is_resolved())


class TestFindProgramRoot(TestCase):
    @patchfs
    def test_finds_program_higher_in_dir_tree(self, fs):
        program_root = pathlib.Path("foo")
        pwd = program_root / "subprojfoo" / "libbar"
        make_mbed_program_files(program_root, fs)
        fs.create_dir(str(pwd))

        self.assertEqual(_find_program_root(pwd), program_root.resolve())

    @patchfs
    def test_finds_program_at_current_path(self, fs):
        program_root = pathlib.Path("foo")
        make_mbed_program_files(program_root, fs)

        self.assertEqual(_find_program_root(program_root), program_root.resolve())

    @patchfs
    def test_raises_if_no_program_found(self, fs):
        program_root = pathlib.Path("foo")
        fs.create_dir(str(program_root))

        with self.assertRaises(ProgramNotFound):
            _find_program_root(program_root)

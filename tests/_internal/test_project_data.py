#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Tests for project_data.py"""
import pathlib

from unittest import TestCase

from pyfakefs.fake_filesystem_unittest import patchfs

from mbed_project._internal.project_data import MbedProgramData
from tests.factories import make_mbed_lib_reference, make_mbed_program_files


class TestMbedProgramData(TestCase):
    @patchfs
    def test_from_new_raises_if_program_already_exists(self, fs):
        root = pathlib.Path("foo")
        make_mbed_program_files(root, fs)

        with self.assertRaises(ValueError):
            MbedProgramData.from_new(root)

    @patchfs
    def test_from_new_returns_valid_program(self, fs):
        root = pathlib.Path("foo")
        fs.create_dir(str(root))

        program = MbedProgramData.from_new(root)

        self.assertTrue(program.config_file.exists())

    @patchfs
    def test_from_existing_raises_if_program_doesnt_exist(self, fs):
        root = pathlib.Path("foo")
        fs.create_dir(str(root))

        with self.assertRaises(ValueError):
            MbedProgramData.from_existing(root)

    @patchfs
    def test_from_existing_finds_existing_program_data(self, fs):
        root = pathlib.Path("foo")
        make_mbed_program_files(root, fs)

        program = MbedProgramData.from_existing(root)

        self.assertTrue(program.config_file.exists())


class TestMbedLibReference(TestCase):
    @patchfs
    def test_is_resolved_returns_true_if_source_code_dir_exists(self, fs):
        root = pathlib.Path("foo")
        lib = make_mbed_lib_reference(root, fs, resolved=True)

        self.assertTrue(lib.is_resolved())

    @patchfs
    def test_is_resolved_returns_false_if_source_code_dir_doesnt_exist(self, fs):
        root = pathlib.Path("foo")
        lib = make_mbed_lib_reference(root, fs)

        self.assertFalse(lib.is_resolved())

    @patchfs
    def test_get_git_reference_returns_lib_file_contents(self, fs):
        root = pathlib.Path("foo")
        url = "https://github.com/mylibrepo"
        lib = make_mbed_lib_reference(root, fs, ref_url=url)

        self.assertEqual(lib.get_git_reference(), url)

#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from mbed_project._internal.project_data import MbedLibReference


def make_mbed_program_files(root, fs, config_file_name="mbed_app.json"):
    fs.create_dir(str(root))
    fs.create_file(str(root / ".mbed"))
    fs.create_file(str(root / config_file_name))


def make_mbed_lib_reference(root, fs, resolved=False, ref_url=None):
    ref_file = root / "mylib.lib"
    source_dir = ref_file.with_suffix("")
    fs.create_dir(str(root))
    fs.create_file(str(ref_file))
    if resolved:
        fs.create_dir(str(source_dir))

    if ref_url is not None:
        ref_file.write_text(ref_url)

    return MbedLibReference(reference_file=ref_file, source_code_path=source_dir)


def make_mbed_os_files(root, fs):
    fs.create_dir(root)
    fs.create_file(root / "targets.json")

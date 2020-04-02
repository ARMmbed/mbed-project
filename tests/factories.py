#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from mbed_project._internal.project_data import MbedLibReference


def make_mbed_program_files(root, fs, config_file_name="mbed_app.json"):
    if not root.exists():
        fs.create_dir(root)

    fs.create_file(root / ".mbed")
    fs.create_file(root / "mbed-os.lib")
    fs.create_file(root / config_file_name)


def make_mbed_lib_reference(root, fs, name="mylib.lib", resolved=False, ref_url=None):
    ref_file = root / name
    source_dir = ref_file.with_suffix("")
    if not root.exists():
        fs.create_dir(root)

    fs.create_file(ref_file)

    if resolved:
        fs.create_dir(source_dir)

    if ref_url is not None:
        ref_file.write_text(ref_url)

    return MbedLibReference(reference_file=ref_file, source_code_path=source_dir)


def make_mbed_os_files(root, fs):
    if not root.exists():
        fs.create_dir(root)

    fs.create_file(root / "targets" / "targets.json")

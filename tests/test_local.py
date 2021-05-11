# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import os
import shutil
from pathlib import Path
from subprocess import check_call, Popen
from tempfile import TemporaryDirectory
from typing import List

from awscmds import set_header_prefix, print_header
from .common import check_base_url, wait_while_connection_error, top_level_dir, \
    test_project_path, should_run


def test_local(project: str, args_to_python: List[str]):

    set_header_prefix(f"test_local {project} {args_to_python}")
    project_dir = test_project_path(project)

    with TemporaryDirectory() as td:
        temp_project_dir = os.path.join(td, 'proj')
        temp_venv_dir = os.path.join(td, 'venv')
        temp_python = os.path.join(temp_venv_dir, 'bin', 'python')

        print_header('Creating venv & project')
        check_call(('python3', '-m', 'venv', temp_venv_dir))
        check_call((temp_python, '-m', 'pip', 'install', '-U', 'pip'))

        shutil.copytree(project_dir, temp_project_dir)
        check_call((temp_python, '-m', 'pip', 'install', '-r',
                    os.path.join(temp_project_dir, 'requirements.txt')))

        # installing the package itself with setup.py
        with TemporaryDirectory() as copy_of_package_parent:
            # copying the whole lambdorado dir with setup.py
            # to temporary directory (to avoid creation of unnecessary
            # 'build' and 'egg-info' dirs in the source)
            copied_distro_dir = os.path.join(copy_of_package_parent, 'pkg')
            shutil.copytree(str(top_level_dir), copied_distro_dir)
            # installing the lambdorado to virtual environment
            check_call((temp_python, '-m', 'pip', 'install',
                        '--use-feature=in-tree-build',
                        copied_distro_dir))

        print_header('Testing')

        call_args = [temp_python]
        call_args.extend(args_to_python)

        with Popen(call_args,
                   cwd=temp_project_dir) as server:
            wait_while_connection_error('http://127.0.0.1:5000')
            check_base_url('http://127.0.0.1:5000')
            server.terminate()


if __name__ == "__main__":

    # I prefer to call the tests from GitHub Actions one at a time,
    # otherwise the GitHub log is a mess.

    if should_run(1):
        test_local('flask1', ['main.py'])
    if should_run(2):
        test_local('flask2', ['mainmain.py'])
    if should_run(3):
        test_local('flask2', ['-m', 'mainmain'])
    if should_run(4):
        test_local('flask3', ['-m', 'subpkg.mainmain'])

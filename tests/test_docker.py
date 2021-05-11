# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import List

from lambdado_pipeline import set_header_prefix, docker_run, docker_stop
from .common import check_base_url, build_docker_by_template, \
    docker_image_name, wait_while_connection_error


def test_project(project_dir: Path, entrypoint_args: List[str]):
    set_header_prefix(f"test_project {project_dir} {entrypoint_args}")

    build_docker_by_template(project_dir, entrypoint_args)
    container_name = "testing_lambdado_server"

    docker_run(docker_image_name + ":latest",
               container_name=container_name,
               port_host=6000,
               port_docker=5000,
               detach=True)
    try:
        wait_while_connection_error('http://127.0.0.1:6000')
        check_base_url('http://127.0.0.1:6000')
    finally:
        docker_stop(container_name)


if __name__ == "__main__":
    test_project(Path('samples/flask1'), ['main.py'])
    test_project(Path('samples/flask2'), ['mainmain.py'])
    test_project(Path('samples/flask2'), ['-m', 'mainmain'])
    test_project(Path('samples/flask3'), ['-m', 'subpkg.mainmain'])

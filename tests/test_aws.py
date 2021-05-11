# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT
import sys
from pathlib import Path
from typing import List

from lambdado_pipeline import docker_push_to_ecr, \
    lambda_function_update, set_header_prefix, ecr_delete_images_all
from .common import check_base_url, build_docker_by_template, docker_image_name, \
    test_project_path, should_run


def test_project(project: str, entrypoint_args: List[str]):
    project_dir = test_project_path(project)
    set_header_prefix(f"test_project {project_dir} {entrypoint_args}")
    # print("point 1")
    build_docker_by_template(project_dir, entrypoint_args)
    # print("point 2")
    pushed_image_uri = docker_push_to_ecr(
        docker_image_name + ":latest",
        '094879913805.dkr.ecr.us-east-1.amazonaws.com/lambdarado_test:latest')
    # print("point 3")
    lambda_function_update('us-east-1', 'lambdarado_test', pushed_image_uri)
    check_base_url('https://sbh9z7tr30.execute-api.us-east-1.amazonaws.com')


if __name__ == "__main__":

    # I prefer to call the tests from GitHub Actions one at a time,
    # otherwise the GitHub log is a mess.

    if should_run(1):
        test_project('flask1', ['main.py'])

    if should_run(2):
        test_project('flask2', ['mainmain.py'])

    if should_run(3):
        test_project('flask2', ['-m', 'mainmain'])

    if should_run(4):
        test_project('flask3', ['-m', 'subpkg.mainmain'])

    if should_run('cleanup'):
        ecr_delete_images_all(
            '094879913805.dkr.ecr.us-east-1.amazonaws.com/lambdarado_test:latest')

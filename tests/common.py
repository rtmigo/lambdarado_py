# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import os
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

import requests

# Class of different styles
from lambdado_pipeline import docker_build

RED = '\033[31m'
GREEN = '\033[32m'
CRESET = '\033[0m'

docker_image_name = 'lambdado_test'
top_level_dir = Path(__file__).parent.parent


def build_docker_by_template(project_dir: Path, entrypoint_args: List[str]):
    template = Path('samples/Dockerfile').read_text()
    template = template.replace('PROJECTDIR', str(project_dir))
    template = template.replace('ENTRYPOINT_ARGS',
                                ', '.join(f'"{s}"' for s in entrypoint_args))

    with TemporaryDirectory() as temp_dir:
        temp_docker_file = Path(temp_dir) / "Dockerfile"
        print(f"Building from temp {temp_docker_file}")
        temp_docker_file.write_text(template)
        docker_build(top_level_dir, docker_image_name,
                     temp_docker_file)


def wait_while_connection_error(url, timeout=10):
    for _ in range(timeout):
        try:
            requests.get(url)
            return
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            continue


def request_text(url: str) -> str:
    return requests.get(url).text
    # req = urllib.request.Request(url)
    # response = urllib.request.urlopen(req)
    # return response.read().decode('utf8')


def assert_returns(url, expected):
    returned = request_text(url)
    if returned != expected:
        raise AssertionError(f'Returned {returned}, expected {expected}')


def check_base_url(baseurl: str):
    print(f"Testing URL {baseurl}")
    os.system('')  # color support https://stackoverflow.com/a/54955094
    try:
        assert_returns(f'{baseurl}/a', 'AAA')
        assert_returns(f'{baseurl}/b', 'BBB')
        print(f"{GREEN}TEST OK!{CRESET}")
    except AssertionError:
        print(f"{RED}TEST FAILED!{CRESET}")
        raise

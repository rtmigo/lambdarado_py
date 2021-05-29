#!/bin/bash
set -e

python3 -m tests.test_funcs
python3 -m tests.test_local
python3 -m tests.test_docker
python3 -m tests.test_aws


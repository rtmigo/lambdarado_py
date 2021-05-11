#!/bin/bash
set -e

# todo try this https://stackoverflow.com/a/63237009

docker_image_name="testing-lambdock"

function hdr {
  echo
  printf '%*s\n' 80 '' | tr ' ' \#
  echo "  $1"
  printf '%*s\n' 80 '' | tr ' ' \#
  echo
}

initial_dir=$PWD

#DEFAULT_TRAP_COMMAND="header EXITING"

function test_local() {

  hdr "Preparing $1"

  cd "$initial_dir"

  local tmp_project_dir
  local venv_dir

  tmp_project_dir=$(mktemp -d -t ci-XXXXXXXXXX)
  venv_dir="$tmp_project_dir/venv"
  python3 -m venv "$venv_dir"
  source "$venv_dir/bin/activate"
  pip3 install -U pip
  pip3 install . --use-feature=in-tree-build

  cp -R "$1/." "$tmp_project_dir"

  cd "$tmp_project_dir"
  pip3 install -r requirements.txt

  hdr "Starting server $1"

  python "$2" &
  local process_id
  process_id=$!
  echo "SERVER PID $process_id"

  function on_exit() {
      echo "Killing $process_id"
      kill "$process_id" || true
  }
  trap on_exit EXIT

  sleep 1 # time to start the server
  echo
  python3 "$initial_dir/check_http.py"  "http://127.0.0.1:5000"

  hdr "Cleanup $1"
  kill "$process_id" || true
  deactivate
  rm -rf "$tmp_project_dir"
  #open "$tmp_project_dir"
}

function test_docker() {
  local project_source_dir
  project_source_dir="$1"

  cd "$initial_dir"

  docker build -t "$docker_image_name" -f "$project_source_dir/Dockerfile" "$initial_dir"

  function stop_docker() {
    echo "Stopping container"
    docker container stop docker_debug_server
  }
  trap stop_docker EXIT || true
  docker run --rm -d -p 6000:5000 --name docker_debug_server "$docker_image_name"
  # remove '-d' to see docker output

  sleep 3 # time to start the server
  echo
  python3 "$initial_dir/check_http.py" "http://127.0.0.1:6000"
  stop_docker
}

# TODO test image by uploading to AWS cloud
# (there are no nice ways to do a clean test locally)

#function test_lambda() {
#  local project_source_dir
#  project_source_dir="$1"
#
#  cd "$initial_dir"
#
#  docker build -t "$docker_image_name" -f "$project_source_dir/Dockerfile" "$initial_dir"
#
#  function stop_docker() {
#    echo "Stopping container"
#    docker container stop docker_debug_server
#  }
#  trap stop_docker EXIT || true
#  docker run --env AWS_EXECUTION_ENV="AWS_Lambda_python3.8" --rm -p 9000:8080 --name docker_debug_server "$docker_image_name"
#  # remove '-d' to see docker output
#
#  sleep 3 # time to start the server
#  curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{x=1}'
#  echo
#  #python3 "$initial_dir/check_http.py" "http://127.0.0.1:6000"
#  stop_docker
#}




#test_local samples/flask1 main.py
#test_local samples/flask2 mainmain.py

test_lambda "samples/flask1"



#}
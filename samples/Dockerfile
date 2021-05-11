# TEMPLATE: the PROJECTDIR and ENTRYPOINT_ARGS msut be replaced

FROM public.ecr.aws/lambda/python:3.8 AS base-image

# initializing venv
RUN python3 -m venv "/opt/venv"
RUN /opt/venv/bin/python3 -m pip install --upgrade pip

# copying the test app and installing its requrements
COPY PROJECTDIR/. ./
RUN /opt/venv/bin/python3 -m pip install -r ./requirements.txt

# installing the package
COPY ./. /tmp/lambdock_setup/
RUN /opt/venv/bin/python3 -m pip install /tmp/lambdock_setup --use-feature=in-tree-build

ENTRYPOINT ["/opt/venv/bin/python3", ENTRYPOINT_ARGS]

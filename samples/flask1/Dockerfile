
FROM public.ecr.aws/lambda/python:3.8 AS base-image
#ARG SOURCE_DIR="../../.."


#COPY ./* ./
#COPY ../../lambdock ./

RUN python3 -m venv "/opt/venv"

RUN /opt/venv/bin/python3 -m pip install --upgrade pip

# copying the test app and installing its requrements
COPY samples/flask1/. ./
RUN /opt/venv/bin/python3 -m pip install -r ./requirements.txt

# installing the package
COPY ./. /tmp/lambdock_setup/
RUN /opt/venv/bin/python3 -m pip install /tmp/lambdock_setup  --use-feature=in-tree-build


ENTRYPOINT ["/opt/venv/bin/python3", "main.py"]

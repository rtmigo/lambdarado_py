# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

import os
import sys
import json
import inspect
from typing import Callable, Any, Dict
from types import ModuleType
from aws_lambda_context import LambdaContext

from apig_wsgi import make_lambda_handler
from awslambdaric.__main__ import main as ric_main


def is_called_by_awslambdaric() -> bool:
    """Returns True when the current function is called by `awslambdaric`
    module. This happens when awslambdaric is importing the lambda handler
    and the `is_called_by_awslambdaric` is called by the module that defines
    the handler.
    """
    for frame in inspect.stack():
        # /opt/venv/lib/python3.8/site-packages/awslambdaric/bootstrap.py
        if frame.filename.startswith('<frozen'):
            continue
        if os.path.basename(os.path.dirname(frame.filename)) == 'awslambdaric':
            return True
    return False


def caller_module() -> ModuleType:
    frame = inspect.currentframe().f_back
    while frame is not None:
        module = inspect.getmodule(frame)
        if module.__file__ != __file__:
            return module
        frame = frame.f_back
    raise RuntimeError


def file_to_module_name(module: ModuleType) -> str:
    file_absolute = os.path.abspath(module.__file__)
    # print(f"file_abspath {file_absolute}")
    assert os.path.exists(file_absolute)

    file_relative = os.path.relpath(
        file_absolute,
        os.path.abspath(sys.path[0]))

    assert file_relative.lower().endswith('.py')

    module_name = file_relative[:-3]
    module_name = module_name.replace(os.path.sep, '.')

    return module_name


# AWS_LAMBDA_RUNTIME_API AWS_EXECUTION_ENV
_in_aws = os.environ.get("AWS_EXECUTION_ENV") is not None

AwsHandlerFunc = Callable[[Dict, LambdaContext], Dict]
WrapAwsHandlerFunc = Callable[[AwsHandlerFunc], AwsHandlerFunc]


def _wrap_aws_handler_default(handler: AwsHandlerFunc) -> AwsHandlerFunc:
    """Used as a default value for start(wrap_handler=...).

    Creates a handler that will write JSON requests and responses to the
    stdout (i.e. CloudWatch logs). The writing is only happens when either
    LOG_LAMBDA_REQUESTS or LOG_LAMBDA_RESPONSES environment variable is set.
    """
    # todo unit test
    if _wrap_aws_handler_default.log_requests is None:
        _wrap_aws_handler_default.log_requests = \
            str(os.environ.get("LOG_LAMBDA_REQUESTS")) == '0'
        _wrap_aws_handler_default.log_responses = \
            str(os.environ.get("LOG_LAMBDA_RESPONSES")) == '0'

    if _wrap_aws_handler_default.log_requests \
            or _wrap_aws_handler_default.log_responses:
        # if something should be logged
        def wrapper(event: Dict, context: LambdaContext) -> Dict:
            if _wrap_aws_handler_default.log_requests:
                print(json.dumps(event, indent=2, sort_keys=True))
            response = handler(event, context)
            if _wrap_aws_handler_default.log_responses:
                print(json.dumps(response, indent=2, sort_keys=True))
            return response

        return wrapper

    else:
        # do not wrap
        return handler


_wrap_aws_handler_default.log_requests = None
_wrap_aws_handler_default.log_responses = None


def assign_lambda_handler(module_name: str,
                          wsgi_app,
                          wrap_handler: WrapAwsHandlerFunc = None):
    """Defines the global `handler` function in the loaded module
    named `module_name`.

    If the module is not loaded, does nothing.
    If the module already has `handler`, does nothing.

    Otherwise the `handler` is initialized with a function ready to process
    AWS Lambda requests. The requests will be processed with `app`.
    """

    #
    # When we programmatically call `ric_main` with `basename.handler`
    # argument, it will try to import file `basename.py` as module
    # `basename`, and then use the `handler` defined there.
    #
    # The easiest way is just declare the `handler` function inside the
    # `basename.py`.
    #
    # ```
    # def handler(event, context):
    #   pass
    # ```
    #
    #
    # PROBLEM 1
    # ---------
    #
    # We want to keep `basename.py` as simple as possible. We
    # assume, it contains only
    #
    # ```
    #   start(app) # app is Flask
    # ```
    #
    # It means, we have to detect the module, from which the `start`
    # is called (it's `basename`) and dynamically assign the handler
    # to it.
    #
    #
    # PROBLEM 2
    # ---------
    #
    # We also assume, that the `basename.py` is the entrypoint:
    # the Dockerfile runs it as ENTRYPOINT ["python", "basename.py"].
    #
    # So when it executed for the first time (as entrypoint), the
    # `basename.py` has name "__main__". Then ric_main will re-import
    # the same file under name "basename".
    #
    # We have to assign the `handler` to the `basename` module only
    # when it is re-imported by the `ric_main`. Defining `handler` on
    # `__main__` will have to effect.

    if module_name not in sys.modules:
        return
    module = sys.modules.get(module_name)
    if not module:
        return
    if 'handler' in module.__dict__:
        print(f'{module} already has the `handler` defined')
        return

    # noinspection PyTypeChecker
    aws_handler: AwsHandlerFunc = make_lambda_handler(wsgi_app,
                                                      binary_support=True)

    # todo unit test
    if wrap_handler is not None:
        aws_handler = wrap_handler(aws_handler)

    module.__dict__['handler'] = aws_handler


def start(get_app: Callable,
          wrap_handler: WrapAwsHandlerFunc = _wrap_aws_handler_default) -> None:
    """
    Starts serving requests.

    :param get_app: Function that initializes and returns the Flask app.

        def get_app():
            app = Flask(__name__)

            @app.route('/hello')
            def hello():
                return 'Hello, client!'

            return app

        start(get_app)

    :param wrap_handler: An optional function, that will wrap the lambda
    handler, probably adding some additional functionality to each call of the
    lambda function.

        def wrap_my_handler(old_handler):
            def new_handler(event, context):
                print(event['input']['headers'])
                response = old_handler(event, context)
                return response

        start(get_app, wrap_handler = wrap_my_handler)

    :return: None
    """
    module = caller_module()
    module_name = file_to_module_name(module)

    caller_is_main = module.__name__ == "__main__"

    # IN_DOCKER=True when running Docker images locally.
    # For some reason it is False when running in AWS Lambda
    # (deployed as Docker Container)
    in_docker = os.path.exists("/.dockerenv")

    app = get_app()

    app.config['running-in-docker'] = in_docker
    app.config['running-in-aws'] = _in_aws

    if _in_aws:
        assign_lambda_handler(module_name, app, wrap_handler)
        if not is_called_by_awslambdaric():
            arg = f'{module_name}.handler'
            print(f'Starting AWS Lambda RIC with arg "{arg}"')
            ric_main((None, arg))

    elif caller_is_main:
        print("RUNNING!")
        app.run(debug=True, host='0.0.0.0' if in_docker else '127.0.0.1')

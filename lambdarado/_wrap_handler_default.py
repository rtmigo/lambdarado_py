import json
import os
from typing import Dict

from aws_lambda_context import LambdaContext

from lambdarado._common import AwsHandlerFunc


def _is_true_environ(key: str, default: bool = False) -> bool:
    value = os.environ.get(key)
    if value is None:
        return default
    value = value.strip()
    if value.isdigit():
        return int(value) != 0
    value = value.lower()
    if value == 'true':
        return True
    if value == 'false':
        return False
    return default


def wrap_aws_handler_default(handler: AwsHandlerFunc) -> AwsHandlerFunc:
    """Used as a default value for start(wrap_handler=...).

    Creates a handler that will write JSON requests and responses to the
    stdout (i.e. CloudWatch logs). The writing is only happens when either
    LOG_LAMBDA_REQUESTS or LOG_LAMBDA_RESPONSES environment variable is set.
    """

    # todo test it (locally, without aws)

    log_requests = _is_true_environ("LOG_LAMBDA_REQUESTS", default=False)
    log_responses = _is_true_environ("LOG_LAMBDA_RESPONSES", default=False)

    print(f"wrap_aws_handler_default: log_requests={log_requests}")
    print(f"wrap_aws_handler_default: log_responses={log_responses}")

    if log_requests or log_responses:
        # if something should be logged
        def wrapper(event: Dict, context: LambdaContext) -> Dict:
            if log_requests:
                print("-- request start -----------------------------------")
                print(json.dumps(event, indent=2, sort_keys=True))
                print("-- request end -------------------------------------")
            response = handler(event, context)
            if log_responses:
                print("-- response start ----------------------------------")
                print(json.dumps(response, indent=2, sort_keys=True))
                print("-- response end ------------------------------------")
            return response

        return wrapper

    else:
        # do not wrap
        return handler

# wrap_aws_handler_default.log_requests = None
# wrap_aws_handler_default.log_responses = None

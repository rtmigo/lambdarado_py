# SPDX-FileCopyrightText: (c) 2021 Artёm IG <github.com/rtmigo>
# SPDX-License-Identifier: MIT

from aws_lambda_context import LambdaContext
from typing import Callable, Dict

AwsHandlerFunc = Callable[[Dict, LambdaContext], Dict]
WrapAwsHandlerFunc = Callable[[AwsHandlerFunc], AwsHandlerFunc]

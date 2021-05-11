# import os
#
# from awslambdaric.__main__ import main as ric_main
# import importlib
# from argparse import ArgumentParser
#
# _in_aws = os.environ.get("AWS_EXECUTION_ENV") is not None
#
#
# def main_run():
#     parser = ArgumentParser()
#     parser.add_argument('main_module')
#     args = parser.parse_args()
#
#     if not _in_aws:
#         app_main_module = importlib.import_module(args.main_module)
#         app_main_module.__dict__['app'].run()
#     raise NotImplementedError

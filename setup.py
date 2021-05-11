from importlib.machinery import SourceFileLoader
from pathlib import Path
from setuptools import setup

constants = SourceFileLoader('constants',
                             'lambdarado/constants.py').load_module()

setup(
    name="lambdarado",
    version=constants.__dict__['__version__'],
    author="Artёm IG",
    author_email="ortemeo@gmail.com",
    url='https://github.com/rtmigo/lambdarado_py',

    install_requires=['apig_wsgi', 'awslambdaric'],
    packages=['lambdarado'],

    description="Universal entry point for Docker images containing "
                "a WSGI app for the AWS Lambda.",

    keywords="amazon aws lambda function entrypoint docker image container "
             "wsgi flask http api gateway".split(),

    long_description=(Path(__file__).parent / 'README.md').read_text(),
    long_description_content_type='text/markdown',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX",
    ],
)

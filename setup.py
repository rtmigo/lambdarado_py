from pathlib import Path
from setuptools import setup

setup(
    name="lambdarado",
    version="0.0.0",
    
    author="Artёm IG",
    author_email="ortemeo@gmail.com",
    url='https://github.com/rtmigo/lambdarado_py',

    install_requires=['apig_wsgi', 'awslambdaric'],
    packages=['lambdarado'],

    description="Universal entrypoint for containerized AWS Lambda apps",

    long_description=(Path(__file__).parent / 'README.md').read_text(),
    long_description_content_type='text/markdown',

    license='MIT',

    classifiers=[
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX",
    ],
)

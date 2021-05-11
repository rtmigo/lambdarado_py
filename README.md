Universal entry point for Docker images containing a Flask application for the
AWS Lambda serverless platform.

Putting together:

- A web application written in Python that is compliant with the
  [WSGI standard](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface).
  Currently, only **Flask** is supported.
- A [Docker image](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
  that contains the application code and dependencies
- AWS Lambda to run the code contained in the Docker image
- AWS API Gateway, that broadcasts web requests to and from your Lambda function

# What it does

The package runs the relevant code depending on where it runs.

On the local computer, this is the debug server, serving requests to
`127.0.0.1` right in the browser.

In the AWS Cloud, this is the handler that passes Gateway requests to and from
the WSGI application.

# Install

``` bash
$ pip3 install git+https://github.com/rtmigo/lambdarado_py#egg=lambdarado 
```

# Configure

#### Dockerfile:

``` Dockerfile
FROM public.ecr.aws/lambda/python:3.8

# ... here should be the code that creates the image ...

ENTRYPOINT ["python", "main.py"]
```

#### main.py

``` python3
from lambdarado import hybrid_server
from my_app import app  # WSGI app, e.g. Flask
hybrid_server(app)
```

# Run

Local debug server
------------------

Running shell command on development machine:

```
$ python3 main.py
```

This will start Werkzeug server listening to http://127.0.0.1:5000.


Local debug server in Docker
----------------------------

Command-line:

``` bash
$ docker run -p 6000:5000 docker-image-name
```

This will start Werkzeug server listening to http://0.0.0.0:5000
(inside the docker). The server is accessible as http://127.0.0.1:6000
from the host machine.


Production server on AWS Lambda
-------------------------------

After deploying the same image as a Lambda function, it will serve the requests
to the AWS Gateway with your `app`.

- You should connect the AWS Gateway to your Lambda function. For the function
  to receive all HTTP requests, you may need to redirect the `/{proxy+}` route
  to the function and make `lambda:InvokeFunction` policy less restrictive

Under the hood:

- The [awslambdaric](https://pypi.org/project/awslambdaric/) will receive
  requests from and send requests to the Lambda service
- The [apig_wsgi](https://pypi.org/project/apig-wsgi/) will translate requests
  received by `awslambdaric` from the AWS Gateway. So your application doesn't
  have to handle calls from the gateway directly. For the application, requests
  will look like normal HTTP


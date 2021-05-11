Universal entry point for Docker images containing Flask apps for the
AWS Lambda serverless platform.

---

It runs the relevant code depending on where it runs.

On the local computer, it runs
the [debug server](https://pypi.org/project/Werkzeug/), serving requests to
`127.0.0.1` with your `app`. You can start it directly (`python3 main.py`) or from a
container (`docker run ...`) to test the app.

In the AWS Cloud the requests are handled with the same `app`, but in a
different way. Lambdarado creates
a [handler](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html),
that is compatible with the combination of API Gateway + Lambda Function.

---

So the Lambdarado puts together:

- A web application written in Python that is compliant with the
  [WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) standard.
  Currently, only [Flask](https://pypi.org/project/Flask/) is supported

- A [Docker image](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
that contains the app code and dependencies

- AWS Lambda to run the code contained in the Docker image

- AWS API Gateway, that broadcasts web requests to and from your Lambda function

# Install

``` bash
$ pip3 install lambdarado 
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
import lambdarado import start

def get_app():
  # this method must return WSGI app, e.g. Flask
  from my_app_module import app
  return app 
  
start(get_app)
```

When starting the Lambda function instance the `main.py` will be imported 
*twice*, but the `get_app` method will only run *once*. If the creation of 
the `app` object is resource intensive, make sure that it only happens when `get_app` is called.


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
from the development (host) machine.


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


Lambdarado puts together:

- A [Flask](https://pypi.org/project/Flask/) app written in Python

- A [Docker image](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
that contains the app code and dependencies

- AWS Lambda + AWS Gateway to run the app in the AWS

- [Werkzeug](https://pypi.org/project/Werkzeug/) to test app locally 

---

It runs the relevant code depending on where it runs.

On the local computer, it runs
the a debug server, serving requests to
`127.0.0.1` with your `app`. You can start it directly (`python3 main.py`) or from a
container (`docker run ...`) to test the app.

In the AWS Cloud the requests are handled with the same `app`, but in a
different way. Lambdarado creates
a [handler](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html),
that is compatible with the combination of API Gateway + Lambda.

---




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

You build the image [as usual](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html),
but the `ENTRYPOINT` is just a call to a `.py` file in the project root.
And there is no `CMD`.

#### main.py

``` python3
import lambdarado import start

def get_app():
  # this function must return WSGI app, e.g. Flask
  from my_app_module import app
  return app 
  
start(get_app)
```

When starting the Lambda function instance, the `get_app` method will run *once*,
but the `main.py` module will be imported *twice*. Make sure that the app is only created
when `get_app` is called, not when `main.py` is imported.

In other words, simply running `python3 main.py` without calling `start` should 
NOT do anything heavy and probably should not even declare or import the `app`.

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
$ docker run -p 5005:5000 docker-image-name
```

This will start Werkzeug server listening to http://0.0.0.0:5000
(inside the docker). The server is accessible as http://127.0.0.1:5005
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


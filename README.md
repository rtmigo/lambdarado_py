### main.py
``` python
from hybrid_server import hybrid_server
from my_app import app  # WSGI app, e.g. Flask
hybrid_server(app)
```

Local debug server
------------------

Running shell command on development machine:
```
$ python3 main.py
```
The function starts Werkzeug server listening to http://127.0.0.1:5000.


Local debug server in Docker
----------------------------

Dockerfile:
``` Dockerfile
ENTRYPOINT ["python", "main.py"]
```

Command-line:
``` bash
docker run -p 6000:5000 docker-image-name
```

The function starts Werkzeug server listening to http://0.0.0.0:5000 
(inside the docker). The server is accessible as http://127.0.0.1:6000 
from development machine.


Production server on AWS Lambda
-------------------------------

Dockerfile:
``` Dockerfile
ENTRYPOINT ["python", "main.py"]
```

The function will start `awslambdaric` to serve the requests and
define the `main.handler`, right before RIC imports it. 
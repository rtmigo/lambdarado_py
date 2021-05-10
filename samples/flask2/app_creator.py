from flask import Flask


app = Flask(__name__)


@app.route('/hello-server')
def hello_world():
    return 'Hello, Client!'
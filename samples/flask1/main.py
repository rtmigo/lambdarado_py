from flask import Flask
from lambdarado import hybrid_server

app = Flask(__name__)


@app.route('/a')
def get_a():
    return 'AAA'


@app.route('/b')
def get_b():
    return 'BBB'


hybrid_server(app)

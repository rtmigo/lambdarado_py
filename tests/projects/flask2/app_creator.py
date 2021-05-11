from flask import Flask

app = Flask(__name__)


@app.route('/a')
def get_a():
    return 'AAA'


@app.route('/b')
def get_b():
    return 'BBB'

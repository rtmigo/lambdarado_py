from flask import Flask
from lambdarado import start


def get_app():
    app = Flask(__name__)

    @app.route('/a')
    def get_a():
        return 'AAA'

    @app.route('/b')
    def get_b():
        return 'BBB'

    return app


start(get_app)

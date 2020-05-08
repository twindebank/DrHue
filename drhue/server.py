from flask import Flask


def start_server():
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Running!'

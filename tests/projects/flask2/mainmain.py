from lambdarado import start


def get_app():
    from app_creator import app
    return app


#start(get_app)
start(get_app)

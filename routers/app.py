from flask import Flask
from src.routers.auth import user_blueprint
from src.routers.talk import talk_blueprint
from src.routers.download import download_blueprint
from src.routers.Information import information_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    app.register_blueprint(user_blueprint)
    app.register_blueprint(talk_blueprint)
    app.register_blueprint(download_blueprint)
    app.register_blueprint(information_blueprint)
    return app

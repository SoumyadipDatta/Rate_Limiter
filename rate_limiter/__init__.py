
from flask import Flask

from .limiter import register_rate_limiter
from .routes import api


def create_app():
    app = Flask(__name__)
    register_rate_limiter(app)
    app.register_blueprint(api)
    return app

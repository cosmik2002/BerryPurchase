
from flask import Flask, jsonify
from flask_cors import CORS
from flask_marshmallow import Marshmallow
# from app import routes, models
# configuration
DEBUG = True
ma = Marshmallow()


def create_app():
    # instantiate the app
    app = Flask(__name__)
    app.config.from_object(__name__)

    ma.init_app(app)
    # enable CORS
    CORS(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app


import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# import rq
from flask import Flask
from flask_cors import CORS
from flask_marshmallow import Marshmallow
# from flask_dotenv import DotEnv
# from flask_sqlalchemy import SQLAlchemy
# from app import routes, models
# configuration
from flask_sock import Sock
# from redis import Redis
from sqlalchemy.orm import scoped_session

from app.whatsapp import WhatsApp
from config import Config
from database import SessionLocal

DEBUG = True
ma = Marshmallow()
# db = SQLAlchemy()
#env = DotEnv()
wa = WhatsApp()
sock = Sock()

def create_app(config_class=Config):
    # instantiate the app
    app = Flask(__name__)
    app.config.from_object(Config)
    #env.init_app(app)
    sock.init_app(app)
    app.logger.setLevel(logging.INFO)
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/berries.log', maxBytes=1024*1024*5,
                                       backupCount=1)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    # file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(logging.StreamHandler(sys.stdout))

    ma.init_app(app)
    # db.init_app(app)
    app.session = SessionLocal
    # enable CORS
    CORS(app)
    wa.init_app(app)
    # app.redis = Redis.from_url(app.config['REDIS_URL'])
    # app.task_queue = rq.Queue('berries-tasks', connection=app.redis)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    from app.reportsBp import  bp as reports_bp
    app.register_blueprint(reports_bp)

    @app.teardown_appcontext
    def remove_session(*args, **kwargs):
        app.session.close()

    return app



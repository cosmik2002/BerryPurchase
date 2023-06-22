import os
from dotenv import load_dotenv
load_dotenv()


class Config(object):
    SQLALCHEMY_DATABASE_URI_REMOTE = os.environ.get('DATABASE_URL_REMOTE') or \
                              'postgresql://postgres:postgres@10.147.18.189/dacha'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///../clients.sqb'
    SQLALCHEMY_DATABASE_URI_NO_FLASK = os.environ.get('DATABASE_URL_NO_FLASK') or os.environ.get('DATABASE_URL') or 'sqlite:///clients.sqb'


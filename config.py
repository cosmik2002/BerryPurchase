import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    SQLALCHEMY_DATABASE_URI_REMOTE = os.environ.get('DATABASE_URL') or \
                              'postgresql://postgres:postgres@10.147.18.189/dacha'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///../clients.sqb'
    SQLALCHEMY_DATABASE_URI_NO_FLASK = 'sqlite:///clients.sqb'

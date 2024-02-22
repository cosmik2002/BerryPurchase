from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config import Config

# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine_remote = create_engine(
    Config.SQLALCHEMY_DATABASE_URI_REMOTE)
SessionMakerRemote = sessionmaker(autocommit=False, autoflush=True, bind=engine_remote)
SessionRemote = scoped_session(SessionMakerRemote)

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI_NO_FLASK)
_SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
SessionLocal = scoped_session(_SessionLocal)

metadata = MetaData()
Base = declarative_base(metadata=metadata)

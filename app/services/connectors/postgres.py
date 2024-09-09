from os import environ
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

schema = environ.get("DB_PG_SCHEMA", "public")
meta = MetaData(schema=schema)
Base = declarative_base(metadata=meta)


class Postgres(object):
    _engine = None
    _smaker = None
    _ssession = None

    @classmethod
    def init_db(cls):
        host = "localhost"
        name = "fever"
        port = 2025
        user = "fever"
        psw = "fever123"
        # host = environ.get('DB_PG_HOST')
        # name = environ.get('DB_PG_NAME')
        # port = environ.get('DB_PG_PORT')
        # user = environ.get('DB_PG_USER')
        # psw = environ.get('DB_PG_PWD')
        cls._engine = create_engine(
            f"postgresql+psycopg2://{user}:{psw}@{host}:{port}/{name}"
        )
        cls._smaker = sessionmaker(
            bind=cls._engine, autoflush=False, autocommit=False,
            expire_on_commit=False
        )
        cls._ssession = scoped_session(cls._smaker)

    @classmethod
    def get_scoped_session(cls):
        try:
            if not cls._ssession:
                cls.init_db()
            return cls._ssession()
        except Exception as e:
            raise Exception(f"app.services.db.get_scoped_session: {str(e)}")

    @classmethod
    def close_scoped_session(cls):
        try:
            cls._ssession.remove()
        except Exception as e:
            raise Exception(f"app.services.db.close_scoped_session: {str(e)}")

    @classmethod
    def get_engine(cls):
        try:
            if not cls._engine:
                cls.init_db()
            return cls._engine
        except Exception as e:
            raise Exception(f"app.services.db.get_engine: {str(e)}")

    @classmethod
    def get_session(cls):
        try:
            if not cls._smaker:
                cls.init_db()
            return cls._smaker()
        except Exception as e:
            raise Exception(f"app.services.db.get_session: {str(e)}")

    @classmethod
    def close_session(cls, dbsession):
        try:
            dbsession.close()
        except Exception as e:
            raise Exception(f"app.services.db.close_session: {str(e)}")

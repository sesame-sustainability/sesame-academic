import contextlib
from datetime import datetime
import sys

from sqlalchemy import create_engine, event, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


class DB():

    def __init__(self):
        self.engine = None
        self.metadata = MetaData()
        self.Base = declarative_base(metadata=self.metadata)
        self.test_session = None

        @event.listens_for(self.Base, 'before_insert', propagate=True)
        def before_insert(mapper, connection, target):
            if hasattr(target, 'created_at'):
                target.created_at = datetime.utcnow()
            if hasattr(target, 'updated_at'):
                target.updated_at = datetime.utcnow()

        @event.listens_for(self.Base, 'before_update', propagate=True)
        def before_update(mapper, connection, target):
            if hasattr(target, 'updated_at'):
                target.updated_at = datetime.utcnow()

    def test_mode_enable(self):
        self.test_session = self.connection()

    def test_mode_disable(self):
        self.test_session.rollback()
        self.test_session.close()
        self.test_session = None

    def connect(self, url):
        if not self.engine:
            self.engine = create_engine(url, pool_size=5, max_overflow=0, pool_recycle=3600)

    def connection(self):
        if self.test_session is None:
            # get new connection from the pool
            return scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine, expire_on_commit=False))
        else:
            # nested transaction that we'll roll back
            self.test_session.begin_nested()
            return self.test_session

    @contextlib.contextmanager
    def session(self):
        session = self.connection()

        # convenience for querying through models
        self.Base.query = session.query_property()

        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            if self.test_session is None:
                # return connection to pool
                session.close()

            self.Base.query = None

    def save(self, instance):
        with self.session() as session:
            session.add(instance)
            session.commit()


sys.modules[__name__] = DB()

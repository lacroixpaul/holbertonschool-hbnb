from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.models import Base

def setup_in_memory_db():
    """
    Configure une base de données SQLite en mémoire pour les tests.
    """
    engine = create_engine('sqlite:///:memory:', echo=False)

    Base.metadata.create_all(engine)

    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    return Session, engine

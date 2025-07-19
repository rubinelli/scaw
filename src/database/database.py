from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# The engine is now a global variable that can be re-initialized.
engine = None
SessionLocal = None


def init_engine(db_path: str):
    """Initializes the database engine for the given database file."""
    global engine, SessionLocal
    database_url = f"sqlite:///{db_path}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Provides a database session from the currently initialized engine.
    Raises an exception if the engine is not initialized.
    """
    if not SessionLocal:
        raise Exception("Database engine not initialized. Call init_engine() first.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def dispose_engine():
    """Explicitly disposes of the current engine's connection pool."""
    if engine:
        engine.dispose()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///active_game.db"

# This engine is a long-lived, global object that maintains a connection pool.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Provides a database session, ensuring it's closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def dispose_engine():
    """Explicitly disposes of the engine's connection pool.
    This is necessary to release file locks before operations like deletion.
    """
    engine.dispose()
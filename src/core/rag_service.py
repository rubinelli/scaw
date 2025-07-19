"""
This module provides a service for interacting with the Cognee RAG system.
"""

from cognee.core import Cognee
from cognee.modules.search.vector_search import VectorSearch
from sqlalchemy.orm import Session
from database.models import LogEntry


class RAGService:
    """A service for managing the Cognee RAG system."""

    def __init__(self, db_session: Session):
        """Initializes the RAG service."""
        self.db_session = db_session
        self.cognee = Cognee(
            search_engine=VectorSearch,
            vector_database_provider="lancedb",
        )

    def load_adventure_log(self):
        """Loads the adventure log from the database into Cognee."""
        log_entries = self.db_session.query(LogEntry).all()
        documents = [entry.content for entry in log_entries]
        self.cognee.add(documents)

    def search(self, query: str, limit: int = 3) -> list[str]:
        """Searches the knowledge base for relevant information."""
        results = self.cognee.search(query, limit=limit)
        return [result["text"] for result in results]

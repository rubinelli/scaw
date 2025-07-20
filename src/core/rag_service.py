"""
This module provides a service for interacting with the RAG system.
"""
import os
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sqlalchemy.orm import Session
from database.models import LogEntry


class RAGService:
    """A service for managing the RAG system."""

    def __init__(self, db_session: Session):
        """Initializes the RAG service."""
        self.db_session = db_session
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.environ["GOOGLE_API_KEY"],
            transport="rest",
        )
        self.vector_store = Chroma(
            embedding_function=self.embeddings, persist_directory="./chroma_db"
        )

    def load_adventure_log(self):
        """Loads the adventure log from the database into ChromaDB."""
        log_entries = self.db_session.query(LogEntry).all()
        documents = [Document(page_content=entry.content) for entry in log_entries]
        if documents:
            self.vector_store.add_documents(documents)

    def search(self, query: str, limit: int = 3) -> list[str]:
        """Searches the knowledge base for relevant information."""
        results = self.vector_store.similarity_search(query, k=limit)
        return [doc.page_content for doc in results]
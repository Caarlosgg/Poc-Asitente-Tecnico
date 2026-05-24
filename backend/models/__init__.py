"""Modelos ORM — importa todos para facilitar las migraciones."""

from models.vehicle import Vehicle
from models.session import Session, SessionState
from models.message import Message
from models.decision_log import DecisionLog
from models.feedback import Feedback
from models.knowledge import FAQ, DiagnosticTree, HistoricalCase
from models.knowledge_chunk import KnowledgeChunk, EmbeddingJob

__all__ = [
    "Vehicle",
    "Session",
    "SessionState",
    "Message",
    "DecisionLog",
    "Feedback",
    "FAQ",
    "DiagnosticTree",
    "HistoricalCase",
    "KnowledgeChunk",
    "EmbeddingJob",
]

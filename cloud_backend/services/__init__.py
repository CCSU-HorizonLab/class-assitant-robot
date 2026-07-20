"""Database services and repositories."""
from __future__ import annotations

from ..config import Settings
from .base_repository import ResultRepository
from .sqlite_service import FileResultRepository, SQLiteResultRepository
from .postgres_service import PostgreSQLResultRepository


def build_query_repository(
    settings: Settings,
    raw_repository: FileResultRepository,
) -> ResultRepository:
    """Select the active query repository without changing API handlers."""
    backend_name = settings.db_backend.strip().lower()
    if backend_name == "sqlite":
        return SQLiteResultRepository(settings, raw_repository)
    if backend_name == "postgres":
        return PostgreSQLResultRepository(settings, raw_repository)
    return raw_repository


__all__ = [
    "ResultRepository",
    "FileResultRepository",
    "SQLiteResultRepository",
    "PostgreSQLResultRepository",
    "build_query_repository",
]

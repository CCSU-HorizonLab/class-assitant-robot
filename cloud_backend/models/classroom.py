"""Classroom and analysis result models for SQLAlchemy."""
from __future__ import annotations

from sqlalchemy import Column, BigInteger, String, Float, Integer, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from .base import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    classroom_id = Column(String, nullable=False)
    analysis_id = Column(String, unique=True, nullable=False)
    video_id = Column(String, nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=True)
    generated_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    raw_json_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    analysis_results = relationship("AnalysisResult", back_populates="session")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    analysis_id = Column(String, unique=True, nullable=False)
    session_id = Column(BigInteger, ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    classroom_id = Column(String, nullable=True)
    schema_version = Column(String, nullable=True)
    source_kind = Column(String, nullable=False, default="raw")
    source_path = Column(String, nullable=False)
    source_host = Column(String, nullable=True)
    generated_at = Column(DateTime(timezone=True), nullable=True)
    feedback_score = Column(Float, nullable=True)
    attention_score = Column(Float, nullable=True)
    response_score = Column(Float, nullable=True)
    classroom_name = Column(String, nullable=True)
    lesson_title = Column(String, nullable=True)
    status = Column(String, nullable=False, default="raw")
    payload_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)

    session = relationship("Session", back_populates="analysis_results")


class ClassroomResult(Base):
    """SQLite-specific table schema model."""
    __tablename__ = "classroom_results"

    analysis_id = Column(String, primary_key=True)
    classroom_id = Column(String, nullable=False)
    video_id = Column(String, nullable=True)
    schema_version = Column(String, nullable=True)
    source_kind = Column(String, nullable=False)
    source_path = Column(String, nullable=False)
    source_host = Column(String, nullable=True)
    recorded_at = Column(String, nullable=True)
    generated_at = Column(String, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    feedback_score = Column(Float, nullable=True)
    attention_score = Column(Float, nullable=True)
    response_score = Column(Float, nullable=True)
    teacher_question_count = Column(Integer, nullable=True)
    avg_attention_ratio = Column(Float, nullable=True)
    response_success_rate = Column(Float, nullable=True)
    summary_text = Column(String, nullable=True)
    payload_json = Column(String, nullable=False)
    created_at = Column(String, nullable=False)

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from .database import Base


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, nullable=False)
    dm_message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    event_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DMJob(Base):
    __tablename__ = "dm_jobs"
    __table_args__ = (
        UniqueConstraint('user_id', 'rule_id', name='uq_user_rule'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    rule_id = Column(Integer, index=True, nullable=False)
    comment_id = Column(String, index=True, nullable=False)
    message = Column(String, nullable=False)
    status = Column(String, default="queued", index=True)  # queued, processing, sent, delivered, failed, cancelled
    retry_count = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    last_attempt = Column(DateTime, nullable=True)
    dm_id = Column(String, nullable=True, index=True)
    idempotency_key = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class BlockedDuplicate(Base):
    __tablename__ = "blocked_duplicates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    rule_id = Column(Integer, nullable=False)
    comment_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DeletedComment(Base):
    __tablename__ = "deleted_comments"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

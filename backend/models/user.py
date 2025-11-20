"""
User database model.
"""
from datetime import datetime
from sqlalchemy import Column, String, BigInteger, DateTime, Integer, Float, JSON
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    """Represents a Discord user being tracked."""

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    discord_user_id = Column(String(20), unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=False)
    joined_at = Column(DateTime, nullable=True)
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_messages = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    churn_probability = Column(Float, default=0.0)
    flags = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    messages = relationship("Message", back_populates="user")
    risk_assessments = relationship("RiskAssessment", back_populates="user")
    alerts = relationship("Alert", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

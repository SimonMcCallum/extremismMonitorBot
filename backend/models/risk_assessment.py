"""
Risk Assessment database model.
"""
from datetime import datetime
from sqlalchemy import Column, String, BigInteger, DateTime, Float, JSON, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class RiskAssessment(Base):
    """Represents a risk assessment for a message."""

    __tablename__ = "risk_assessments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, ForeignKey("messages.id"), nullable=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    server_id = Column(BigInteger, ForeignKey("servers.id"), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    risk_category = Column(String(100), nullable=True)
    indicators = Column(JSON, nullable=False, default={})
    ai_analysis = Column(Text, nullable=True)
    flagged = Column(Boolean, default=False, index=True)
    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(BigInteger, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    message = relationship("Message", back_populates="risk_assessment")
    user = relationship("User", back_populates="risk_assessments")

    def __repr__(self):
        return f"<RiskAssessment(id={self.id}, risk_score={self.risk_score})>"

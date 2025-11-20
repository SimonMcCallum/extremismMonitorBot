"""
Alert database model.
"""
from datetime import datetime
from sqlalchemy import Column, String, BigInteger, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Alert(Base):
    """Represents an alert for moderators."""

    __tablename__ = "alerts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    server_id = Column(BigInteger, ForeignKey("servers.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    assessment_id = Column(BigInteger, ForeignKey("risk_assessments.id"), nullable=True)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="open", index=True)  # open, acknowledged, resolved
    assigned_to = Column(BigInteger, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    server = relationship("Server", back_populates="alerts")
    user = relationship("User", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, severity='{self.severity}', status='{self.status}')>"

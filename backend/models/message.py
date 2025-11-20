"""
Message database model.
"""
from datetime import datetime
from sqlalchemy import Column, String, BigInteger, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Message(Base):
    """Represents a Discord message."""

    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    discord_message_id = Column(String(20), unique=True, nullable=False, index=True)
    server_id = Column(BigInteger, ForeignKey("servers.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    channel_id = Column(String(20), nullable=False)
    content = Column(Text, nullable=True)
    attachments = Column(JSON, default=[])
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    server = relationship("Server", back_populates="messages")
    user = relationship("User", back_populates="messages")
    risk_assessment = relationship("RiskAssessment", back_populates="message", uselist=False)

    def __repr__(self):
        return f"<Message(id={self.id}, user_id={self.user_id})>"

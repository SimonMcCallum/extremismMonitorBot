"""
Server/Guild database model.
"""
from datetime import datetime
from sqlalchemy import Column, String, BigInteger, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship

from database import Base


class Server(Base):
    """Represents a Discord server/guild."""

    __tablename__ = "servers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    discord_server_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    owner_id = Column(String(20), nullable=False)
    settings = Column(JSON, default={})
    subscription_tier = Column(String(50), default="basic")
    features_enabled = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    messages = relationship("Message", back_populates="server")
    alerts = relationship("Alert", back_populates="server")

    def __repr__(self):
        return f"<Server(id={self.id}, name='{self.name}')>"

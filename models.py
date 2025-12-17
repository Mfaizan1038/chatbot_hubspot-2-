from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    action = Column(String, nullable=True)
    step = Column(String, nullable=True)
    data = Column(JSON, default={})

    contracts = relationship("Contract", back_populates="session")


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    email = Column(String)
    name = Column(String)
    phone = Column(String)
    address = Column(Text)
    status = Column(String, default="PENDING")

    session = relationship("ChatSession", back_populates="contracts")

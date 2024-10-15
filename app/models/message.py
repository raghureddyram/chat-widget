from sqlalchemy import Column, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import ENUM

class MessageType(PyEnum):
    USER = "user"
    SYSTEM = "system"

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey('chats.id'), nullable=False)
    content = Column(Text, nullable=False)
    line_type = Column(ENUM(MessageType), nullable= False)
    created_date = Column(DateTime, default=func.now()) 
    
    chat = relationship("Chat", back_populates="messages")
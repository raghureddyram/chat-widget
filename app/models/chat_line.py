from sqlalchemy import Column, String, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base
from enum import Enum as PyEnum

class ChatLineType(PyEnum):
    USER = "user"
    SYSTEM = "system"

class ChatLine(Base):
    __tablename__ = "chat_lines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey('chats.id'), nullable=False)
    content = Column(Text, nullable=False)
    line_type = Column(Enum(ChatLineType), nullable=False)
    
    chat = relationship("Chat", back_populates="chat_lines")
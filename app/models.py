from sqlalchemy import Column, String, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Enum for chat line types
from enum import Enum as PyEnum

class ChatLineType(PyEnum):
    USER = "user"
    SYSTEM = "system"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    
    # One user can have many chats
    chats = relationship("Chat", back_populates="user")

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    
    user = relationship("User", back_populates="chats")
    chat_lines = relationship("ChatLine", back_populates="chat")

class ChatLine(Base):
    __tablename__ = "chat_lines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey('chats.id'), nullable=False)
    content = Column(Text, nullable=False)
    line_type = Column(Enum(ChatLineType), nullable=False)
    
    chat = relationship("Chat", back_populates="chat_lines")

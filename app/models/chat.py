from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import ENUM

class ChatContextType(PyEnum):
    OTHER = "Other"
    ONBOARDING = "Onboarding"
    SALES = "Sales"
class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    context = Column(ENUM(ChatContextType),nullable= False)
    created_date = Column(DateTime, default=func.now()) 
    
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat")
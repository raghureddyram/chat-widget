from requests import Session
from sqlalchemy import Column, ForeignKey, DateTime, and_
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .message import Message, MessageType
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
    context = Column(ENUM(ChatContextType), nullable= False)
    created_date = Column(DateTime, default=func.now()) 
    
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat")

    @classmethod
    def get_or_create(cls, db: Session, user_id: str, context: ChatContextType):
        chat = db.query(cls).filter(
            and_(cls.user_id == user_id, cls.context == context)
        ).first()
        if not chat:
            chat = cls(user_id=user_id, context=context)
            db.add(chat)
            db.commit()
            db.refresh(chat)
        return chat

    def get_messages(self, db: Session):
        return db.query(Message).filter(Message.chat_id == self.id).all()

    def add_message(self, db: Session, content: str, line_type: MessageType):
        message = Message(chat_id=self.id, content=content, line_type=line_type)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
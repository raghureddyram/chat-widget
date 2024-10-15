from requests import Session
from sqlalchemy import Column, String, DateTime, and_
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .chat import Chat, ChatContextType
from .user_file import UserFile
from .base import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_date = Column(DateTime, default=func.now()) 
    
    # One user can have many chats
    chats = relationship("Chat", back_populates="user")
    user_files = relationship("UserFile", back_populates="user")
    
    @classmethod
    def get_by_id(cls, db: Session, user_id: str):
        return db.query(cls).filter(cls.id == user_id).first()

    def get_or_create_chat(self, db: Session, context: ChatContextType):
        chat = db.query(Chat).filter(
            and_(Chat.user_id == self.id, Chat.context == context)
        ).first()
        if not chat:
            chat = Chat(user_id=self.id, context=context)
            db.add(chat)
            db.commit()
            db.refresh(chat)
        return chat

    def get_file(self, db: Session, file_id: str):
        return db.query(UserFile).filter(
            and_(UserFile.user_id == self.id, UserFile.id == file_id)
        ).first()
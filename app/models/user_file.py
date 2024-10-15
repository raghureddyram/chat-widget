from sqlalchemy import Column, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base


class UserFile(Base):
    __tablename__ = "user_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    file_name = Column(String, nullable=False)
    created_date = Column(DateTime, default=func.now()) 
    
    user = relationship("User", back_populates="user_files")
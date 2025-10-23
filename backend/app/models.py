from sqlalchemy import Column, Integer, String , DateTime, ForeignKey, UniqueConstraint
from .database import Base
import datetime


class Visitor(Base):
    __tablename__ = 'visitors'

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, index=True)
    email = Column(String, index=True)
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    judge_status = Column(String(50), nullable=True, default=None)

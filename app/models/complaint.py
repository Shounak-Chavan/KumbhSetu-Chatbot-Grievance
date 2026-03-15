from sqlalchemy import (
    Column,
    Float,
    String,
    Text,
    Integer,
    DateTime,
)
from sqlalchemy.sql import func
from app.db.base import Base

from datetime import datetime

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    status = Column(String(50), default="Pending Verification")
    department = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
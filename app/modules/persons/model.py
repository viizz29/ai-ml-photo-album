from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, BigInteger
from sqlalchemy.orm import relationship

from app.core.database import Base


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=True)
    face_image_path = Column(String, nullable=False, unique=True)
    encoding = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


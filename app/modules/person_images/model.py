from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, BigInteger
from sqlalchemy.orm import relationship

from app.core.database import Base


class PersonImage(Base):
    __tablename__ = "person_images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False, index=True)
    top = Column(Integer, nullable=False)
    right = Column(Integer, nullable=False)
    bottom = Column(Integer, nullable=False)
    left = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    
    image = relationship("Image", back_populates="person_images")

    

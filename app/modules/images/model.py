from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, BigInteger
from sqlalchemy.orm import relationship

from app.core.database import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False, unique=True)
    content_type = Column(String, nullable=True)
    commentary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    person_images = relationship(
        "PersonImage",
        back_populates="image",
        cascade="all, delete-orphan",
    )
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, BigInteger
from sqlalchemy.orm import relationship

from app.core.database import Base


class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)



class AlbumImage(Base):
    __tablename__ = "album_images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

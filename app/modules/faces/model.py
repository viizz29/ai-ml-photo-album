from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class FaceImage(Base):
    __tablename__ = "face_images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False, unique=True)
    content_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    recognized_faces = relationship(
        "RecognizedFace",
        back_populates="image",
        cascade="all, delete-orphan",
    )


class RecognizedFace(Base):
    __tablename__ = "recognized_faces"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("face_images.id"), nullable=False, index=True)
    person_id = Column(String, nullable=False, index=True)
    encoding = Column(Text, nullable=False)
    top = Column(Integer, nullable=False)
    right = Column(Integer, nullable=False)
    bottom = Column(Integer, nullable=False)
    left = Column(Integer, nullable=False)
    matched_face_id = Column(Integer, ForeignKey("recognized_faces.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    image = relationship("FaceImage", back_populates="recognized_faces")
    matched_face = relationship("RecognizedFace", remote_side=[id], uselist=False)

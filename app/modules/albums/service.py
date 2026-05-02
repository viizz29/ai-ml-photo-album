import json
import os
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings

from .model import Album

class AlbumService:
    def get_albums(self, db: Session, user_id: int):
        return db.query(Album).filter(Album.user_id == user_id).order_by(Album.created_at.desc()).all()

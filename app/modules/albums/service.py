import json
import os
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings

from .model import Album

class AlbumService:
    def get_albums(self, db: Session):
        return db.query(Album).order_by(Album.created_at.desc()).all()

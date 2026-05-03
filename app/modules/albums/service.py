from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.images.model import Image

from .model import Album, AlbumImage

class AlbumService:
    def get_albums(self, db: Session, user_id: int):
        return db.query(Album).filter(Album.user_id == user_id).order_by(Album.created_at.desc()).all()

    def _get_album(self, db: Session, user_id: int, album_id: int):
        album = (
            db.query(Album)
            .filter(Album.id == album_id, Album.user_id == user_id)
            .first()
        )
        if album is None:
            raise HTTPException(status_code=404, detail="Album not found")
        return album
    
    
    def get_album(self, db: Session, user_id: int, album_id: int):
        return self._get_album(db, user_id, album_id)
    

    def get_album_images(
        self,
        db: Session,
        user_id: int,
        album_id: int,
        page: int = 1,
        limit: int = 20,
    ):
        self._get_album(db, user_id, album_id)

        base_query = (
            db.query(Image)
            .join(AlbumImage, AlbumImage.image_id == Image.id)
            .filter(
                AlbumImage.album_id == album_id,
                AlbumImage.user_id == user_id,
                Image.user_id == user_id,
            )
        )

        total = base_query.count()
        offset = (page - 1) * limit
        items = (
            base_query
            .order_by(AlbumImage.created_at.desc(), AlbumImage.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return {
            "items": items,
            "page": page,
            "limit": limit,
            "total": total,
        }

    def remove_album_images(
        self,
        db: Session,
        user_id: int,
        album_id: int,
        image_ids: list[int],
    ):
        self._get_album(db, user_id, album_id)

        unique_image_ids = list(dict.fromkeys(image_ids))
        if not unique_image_ids:
            raise HTTPException(status_code=400, detail="At least one image id is required")

        removed_count = (
            db.query(AlbumImage)
            .filter(
                AlbumImage.album_id == album_id,
                AlbumImage.user_id == user_id,
                AlbumImage.image_id.in_(unique_image_ids),
            )
            .delete(synchronize_session=False)
        )

        db.commit()

        return {
            "removed_count": removed_count,
        }
    
    def create_album(self, db: Session, user_id: int, title: str, search: str | None = None):
        album = Album(user_id=user_id, title=title)
        db.add(album)

        db.flush()

        normalized_search = search.strip() if search else None
        if normalized_search:
            matching_images = (
                db.query(Image.id)
                .filter(
                    Image.user_id == user_id,
                    Image.commentary.ilike(f"%{normalized_search}%"),
                )
                .all()
            )

            for image_id, in matching_images:
                db.add(
                    AlbumImage(
                        user_id=user_id,
                        album_id=album.id,
                        image_id=image_id,
                    )
                )

        db.commit()
        db.refresh(album)
        return album

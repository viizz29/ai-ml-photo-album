from typing import Annotated

from fastapi import APIRouter, Body, Depends, File, Security, UploadFile, Query
from sqlalchemy.orm import Session

from app.core.routing import HashIdRoute
from app.core.schema import HashIdParam
from app.modules.auth.dependencies import get_current_user, get_db
from app.modules.auth.model import User
from .schema import AlbumCreateDto

from .schema import (
    AlbumImagesPageResponseDto,
    RemoveAlbumImagesDto,
    RemoveAlbumImagesResponseDto,
)
from .service import AlbumService

router = APIRouter(prefix="/v1/albums", tags=["albums"], route_class=HashIdRoute)
service = AlbumService()



@router.get("")
def get_list(db: Session = Depends(get_db), current_user: User = Security(get_current_user),):
    return service.get_albums(db, current_user.id)


@router.post("")
def create_album(
    dto: AlbumCreateDto = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
):
    title = dto.title
    search = dto.search
    return service.create_album(db, current_user.id, title, search=search)


@router.get("/{album_id}")
def get_album(
    album_id: HashIdParam,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
):
    return service.get_album(
        db,
        current_user.id,
        album_id=album_id,
    )

@router.get("/{album_id}/images", response_model=AlbumImagesPageResponseDto)
def get_album_images(
    album_id: HashIdParam,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
):
    return service.get_album_images(
        db,
        current_user.id,
        album_id=album_id,
        page=page,
        limit=limit,
    )


@router.delete("/{album_id}/images", response_model=RemoveAlbumImagesResponseDto)
def remove_album_images(
    album_id: HashIdParam,
    dto: RemoveAlbumImagesDto = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
):
    return service.remove_album_images(
        db,
        current_user.id,
        album_id=album_id,
        image_ids=dto.image_ids,
    )

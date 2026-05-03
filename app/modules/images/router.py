from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, Security, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.routing import HashIdRoute
from app.core.schema import HashIdParam
from app.modules.auth.dependencies import get_current_user, get_db
from app.modules.auth.model import User

from .schema import ImageListResponseDto, ImageResponseDto, RandomImageResponseDto
from .service import ImagesService

router = APIRouter(prefix="/v1/images", tags=["images"], route_class=HashIdRoute)
service = ImagesService()


@router.post("", response_model=ImageResponseDto)
def process_and_store(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
):
    return service.process_and_store(db, image, current_user.id)


@router.get("", response_model=ImageListResponseDto)
def get_images(
    search: Annotated[str | None, Query()] = None,
    cursor_id: Annotated[int | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
):
    return service.list_images(
        db,
        current_user.id,
        search=search,
        cursor_id=cursor_id,
        limit=limit,
    )


@router.get("/random", response_model=RandomImageResponseDto)
def get_random_image(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
):
    return service.get_random_image(db, current_user.id)


@router.get("/{image_id}", response_model=ImageResponseDto)
def get_image(image_id: HashIdParam, db: Session = Depends(get_db), current_user: User = Security(get_current_user)):
    return service.get_image(db, current_user.id, image_id)


@router.get("/{image_id}/file")
def get_image_file(
    image_id: HashIdParam,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
):
    image = service.get_image_file(db, current_user.id, image_id)
    return FileResponse(
        path=image.stored_path,
        media_type=image.content_type or "application/octet-stream",
        filename=image.filename,
    )


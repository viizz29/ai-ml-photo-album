from fastapi import APIRouter, Depends, File, Security, UploadFile
from sqlalchemy.orm import Session

from app.core.routing import HashIdRoute
from app.core.schema import HashIdParam
from app.modules.auth.dependencies import get_current_user, get_db
from app.modules.auth.model import User

from .schema import ImageResponseDto, RandomImageResponseDto
from .service import ImagesService

router = APIRouter(prefix="/images", tags=["images"], route_class=HashIdRoute)
service = ImagesService()


@router.post("", response_model=ImageResponseDto)
def upload(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
):
    return service.recognize_and_store(db, image, current_user.id)


@router.get("", response_model=list[ImageResponseDto])
def get_images(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
):
    items =  service.list_images(db)
    return items


@router.get("/random", response_model=RandomImageResponseDto)
def get_random_image(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
):
    return service.get_random_image(db, current_user.id)


@router.get("/{image_id}", response_model=ImageResponseDto)
def get_image(image_id: HashIdParam, db: Session = Depends(get_db), current_user: User = Security(get_current_user)):
    return service.get_image(db, image_id)

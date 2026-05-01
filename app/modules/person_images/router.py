from io import BytesIO

from fastapi import APIRouter, Depends, Security
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.routing import HashIdRoute
from app.modules.auth.dependencies import get_current_user, get_db
from app.modules.auth.model import User

from .service import PersonImagesService
from .schema import PersonImageResponseDto
from app.core.schema import HashIdParam

router = APIRouter(prefix="/person-images", tags=["person-images"], route_class=HashIdRoute)
service = PersonImagesService()

# @router.get("",  response_model=list[RecognizedFaceResponseDto])
# def get_person_images(db: Session = Depends(get_db)):
#     return service.list_person_images(db)


@router.get("/{person_id}", response_model=list[PersonImageResponseDto])
def get_images_for_person(person_id: HashIdParam, db: Session = Depends(get_db), current_user: User = Security(get_current_user),):
    return service.get_person_images(db, current_user.id, person_id)


@router.get("/{person_id}/preview")
def get_person_preview(person_id: HashIdParam, db: Session = Depends(get_db), current_user: User = Security(get_current_user)):
    image_bytes = service.get_person_preview_image(db, current_user.id, person_id)
    return StreamingResponse(BytesIO(image_bytes), media_type="image/png")


@router.get("/{person_id}/face")
def get_person_face(person_id: HashIdParam, db: Session = Depends(get_db), current_user: User = Security(get_current_user)):
    image_bytes = service.get_person_face_image(db, current_user.id, person_id)
    return StreamingResponse(BytesIO(image_bytes), media_type="image/png")

from fastapi import APIRouter, Body, Depends, Security
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.routing import HashIdRoute
from app.core.schema import HashIdParam
from app.modules.auth.dependencies import get_current_user, get_db
from app.modules.auth.model import User

from .service import PersonsService
from .schema import PersonResponseDto, UpdatePersonNameDto

router = APIRouter(prefix="/v1/persons", tags=["persons"], route_class=HashIdRoute)
service = PersonsService()

@router.get("",  response_model=list[PersonResponseDto])
def get_persons(db: Session = Depends(get_db), current_user: User = Security(get_current_user),):
    return service.list_persons(db, current_user.id)


@router.get("/{person_id}", response_model=PersonResponseDto)
def get_person(person_id: HashIdParam, db: Session = Depends(get_db), current_user: User = Security(get_current_user),):
    return service.get_person(db, current_user.id, person_id)


@router.get("/{person_id}/face")
def get_person_face(person_id: HashIdParam, db: Session = Depends(get_db), current_user: User = Security(get_current_user),):
    person = service.get_person_face_image(db, current_user.id, person_id)
    return FileResponse(
        path=person.face_image_path,
        media_type="image/png",
        filename=f"person-{person.id}-face.png",
    )


@router.patch("/{person_id}/name", response_model=PersonResponseDto)
def set_person_name(
    person_id: HashIdParam,
    dto: UpdatePersonNameDto = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user),
):
    return service.set_person_name(db, current_user.id, person_id, dto.name)

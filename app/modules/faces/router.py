from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import SessionLocal

from .schema import FaceImageResponseDto, FaceRecognitionResultDto, RecognizedFaceResponseDto
from .service import FaceRecognitionService

router = APIRouter(prefix="/faces", tags=["faces"])
service = FaceRecognitionService()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/recognize", response_model=FaceRecognitionResultDto)
def recognize_faces(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return service.recognize_and_store(db, image)


@router.get("/images", response_model=list[FaceImageResponseDto])
def get_images(db: Session = Depends(get_db)):
    return service.list_images(db)


@router.get("", response_model=list[RecognizedFaceResponseDto])
def get_faces(db: Session = Depends(get_db)):
    return service.list_faces(db)


@router.get("/persons/{person_id}", response_model=list[RecognizedFaceResponseDto])
def get_person_faces(person_id: str, db: Session = Depends(get_db)):
    return service.list_person_faces(db, person_id)

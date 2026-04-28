from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FaceMatchDto(BaseModel):
    matched_face_id: int
    person_id: str
    image_id: int
    distance: float


class RecognizedFaceMatchResultDto(BaseModel):
    face_id: int
    matches: list[FaceMatchDto]


class RecognizedFaceResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_id: int
    person_id: str
    top: int
    right: int
    bottom: int
    left: int
    matched_face_id: int | None
    created_at: datetime


class FaceImageResponseDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    stored_path: str
    content_type: str | None
    created_at: datetime
    recognized_faces: list[RecognizedFaceResponseDto]


class FaceRecognitionResultDto(BaseModel):
    image: FaceImageResponseDto
    matches: list[RecognizedFaceMatchResultDto]

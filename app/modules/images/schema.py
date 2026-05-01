from datetime import datetime

from app.core.schema import CamelCaseSchema


class FaceMatchDto(CamelCaseSchema):
    matched_face_id: int
    person_id: str
    image_id: int
    distance: float


class RecognizedFaceMatchResultDto(CamelCaseSchema):
    face_id: int
    matches: list[FaceMatchDto]


class RecognizedFaceResponseDto(CamelCaseSchema):
    id: int
    image_id: int
    person_id: str
    top: int
    right: int
    bottom: int
    left: int
    matched_face_id: int | None
    created_at: datetime


class ImageResponseDto(CamelCaseSchema):
    id: int
    filename: str
    stored_path: str
    content_type: str | None
    created_at: datetime


class RandomImageResponseDto(ImageResponseDto):
    commentary: str


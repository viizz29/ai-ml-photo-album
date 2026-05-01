from datetime import datetime

from app.core.schema import CamelCaseSchema



class PersonImageResponseDto(CamelCaseSchema):
    id: int
    user_id: int
    person_id: int
    image_id: int
    top: int
    right: int
    bottom: int
    left: int
    created_at: datetime


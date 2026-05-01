from datetime import datetime

from app.core.schema import CamelCaseSchema


class UpdatePersonNameDto(CamelCaseSchema):
    name: str



class PersonResponseDto(CamelCaseSchema):
    id: int
    user_id: int
    name: str | None
    created_at: datetime

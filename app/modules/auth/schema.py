# =========================
# modules/auth/schema.py
# =========================
from pydantic import BaseModel


class RegisterDto(BaseModel):
    email: str
    name: str
    password: str


class LoginDto(BaseModel):
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user1@example.com",
                "password": "password123",
            }
        }
    }

    email: str
    password: str


class UserResponseDto(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


class LoginResponseDto(BaseModel):
    access_token: str
    user: UserResponseDto

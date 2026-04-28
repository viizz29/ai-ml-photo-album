# =========================
# modules/auth/schema.py
# =========================
from pydantic import BaseModel

class RegisterDto(BaseModel):
    email: str
    password: str

class LoginDto(BaseModel):
    email: str
    password: str
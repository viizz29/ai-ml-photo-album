from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.routing import HashIdRoute

from .dependencies import get_db
from .schema import LoginDto, LoginResponseDto, RegisterDto, UserResponseDto
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"], route_class=HashIdRoute)
service = AuthService()


@router.post("/register", response_model=UserResponseDto)
def register(dto: RegisterDto, db: Session = Depends(get_db)):
    return service.register(db, dto)


@router.post("/login", response_model=LoginResponseDto)
def login(dto: LoginDto, db: Session = Depends(get_db)):
    return service.login(db, dto)

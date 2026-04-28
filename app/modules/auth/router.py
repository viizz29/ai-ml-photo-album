from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from .schema import RegisterDto, LoginDto
from .service import AuthService

router = APIRouter(prefix="/auth")
service = AuthService()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(dto: RegisterDto, db: Session = Depends(get_db)):
    return service.register(db, dto)


@router.post("/login")
def login(dto: LoginDto, db: Session = Depends(get_db)):
    return service.login(db, dto)
from sqlalchemy.orm import Session
from .model import User
from app.core.security import hash_password, verify_password, create_access_token

class AuthService:
    def register(self, db: Session, dto):
        user = User(email=dto.email, password=hash_password(dto.password))
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def login(self, db: Session, dto):
        user = db.query(User).filter(User.email == dto.email).first()
        if not user or not verify_password(dto.password, user.password):
            return None
        token = create_access_token({"sub": user.email})
        return {"access_token": token}
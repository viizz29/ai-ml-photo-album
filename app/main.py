from fastapi import FastAPI
from app.modules.auth.router import router as auth_router
from app.modules.faces.router import router as faces_router
from app.modules.test.router import router as test_router
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router)
app.include_router(faces_router)
app.include_router(test_router)

from fastapi import FastAPI

from app.core.hashids import HashIdJSONResponse
from app.modules.auth.router import router as auth_router
from app.modules.faces.router import router as faces_router
from app.modules.test.router import router as test_router

app = FastAPI(default_response_class=HashIdJSONResponse)
app.include_router(auth_router)
app.include_router(faces_router)
app.include_router(test_router)

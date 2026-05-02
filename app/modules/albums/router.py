from fastapi import APIRouter, Depends, File, Security, UploadFile
from sqlalchemy.orm import Session

from app.core.routing import HashIdRoute
from app.modules.auth.dependencies import get_current_user, get_db
from app.modules.auth.model import User

from .service import AlbumService

router = APIRouter(prefix="/albums", tags=["albums"], route_class=HashIdRoute)
service = AlbumService()



@router.get("")
def get_list(db: Session = Depends(get_db), current_user: User = Security(get_current_user),):
    return service.get_albums(db, current_user.id)

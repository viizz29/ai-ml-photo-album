from fastapi import APIRouter
from fastapi.responses import FileResponse
import os
import face_recognition
import cv2


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

router = APIRouter(prefix="/test")

@router.get("/test1")
def test1():
    return "test1"


@router.get("/image")
def get_image():
    # print(BASE_DIR)
    file_path = os.path.join(BASE_DIR, "../../images/sample.png")
    return FileResponse(file_path, media_type="image/png")


@router.get("/recognize")
def recognize():
    file_path = os.path.join(BASE_DIR, "../../images/sample.png")
    image = face_recognition.load_image_file(file_path)

    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    str = f"Found {len(face_encodings)} faces"
    return str
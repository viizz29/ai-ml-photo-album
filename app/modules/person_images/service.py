from io import BytesIO

import cv2
import face_recognition
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.images.model import Image
from app.modules.persons.model import Person

from .model import PersonImage

class PersonImagesService:
    def list_person_images(self, db: Session):
        return db.query(PersonImage).order_by(PersonImage.created_at.desc()).all()
    
    def get_person_images(self, db: Session, user_id: int, person_id: int):
        return (
            db.query(PersonImage)
            .filter(PersonImage.user_id == user_id, PersonImage.person_id == person_id)
            .order_by(PersonImage.created_at.desc())
            .all()
        )

    def get_person_preview_image(self, db: Session, user_id: int, person_id: int) -> bytes:
        person, face_record, image_record = self._get_person_image_context(db, user_id, person_id)
        source_image = face_recognition.load_image_file(image_record.stored_path)
        annotated_image = cv2.cvtColor(source_image, cv2.COLOR_RGB2BGR)

        cv2.rectangle(
            annotated_image,
            (face_record.left, face_record.top),
            (face_record.right, face_record.bottom),
            (0, 255, 0),
            3,
        )

        label = person.name or f"Person {person.id}"
        label_y = face_record.top - 10 if face_record.top > 30 else face_record.bottom + 25
        cv2.putText(
            annotated_image,
            label,
            (face_record.left, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        success, encoded_image = cv2.imencode(".png", annotated_image)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to render preview image")

        return BytesIO(encoded_image.tobytes()).getvalue()

    def get_person_face_image(self, db: Session, user_id: int, person_id: int) -> bytes:
        _, face_record, image_record = self._get_person_image_context(db, user_id, person_id)
        source_image = face_recognition.load_image_file(image_record.stored_path)
        annotated_image = cv2.cvtColor(source_image, cv2.COLOR_RGB2BGR)

        image_height, image_width = annotated_image.shape[:2]
        face_width = face_record.right - face_record.left
        face_height = face_record.bottom - face_record.top

        # Expand the crop so we include the full head and a bit of context.
        extra_left = int(face_width * 0.35)
        extra_right = int(face_width * 0.35)
        extra_top = int(face_height * 0.7)
        extra_bottom = int(face_height * 0.45)

        crop_left = max(0, face_record.left - extra_left)
        crop_right = min(image_width, face_record.right + extra_right)
        crop_top = max(0, face_record.top - extra_top)
        crop_bottom = min(image_height, face_record.bottom + extra_bottom)

        cropped_image = annotated_image[crop_top:crop_bottom, crop_left:crop_right]
        if cropped_image.size == 0:
            raise HTTPException(status_code=500, detail="Failed to crop face image")

        success, encoded_image = cv2.imencode(".png", cropped_image)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to render face image")

        return BytesIO(encoded_image.tobytes()).getvalue()

    def _get_person_image_context(self, db: Session, user_id: int, person_id: int):
        person = (
            db.query(Person)
            .filter(Person.id == person_id, Person.user_id == user_id)
            .first()
        )
        if person is None:
            raise HTTPException(status_code=404, detail="Person not found")

        person_image = (
            db.query(PersonImage, Image)
            .join(Image, Image.id == PersonImage.image_id)
            .filter(PersonImage.user_id == user_id, PersonImage.person_id == person_id)
            .order_by(PersonImage.created_at.desc())
            .first()
        )
        if person_image is None:
            raise HTTPException(status_code=404, detail="No images found for person")

        face_record, image_record = person_image
        return person, face_record, image_record

import base64
import json
import os
from pathlib import Path
from urllib import error, request
from uuid import uuid4

import cv2
import face_recognition
from fastapi import HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings

from .model import Image
from app.modules.persons.model import Person
from app.modules.person_images.model import PersonImage


class ImagesService:
    def process_and_store(self, db: Session, image_file: UploadFile, user_id: int):
        if not image_file.filename:
            raise HTTPException(status_code=400, detail="Image filename is required")

        if not image_file.content_type or not image_file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image uploads are supported")

        upload_dir = Path(f"{settings.STORAGE_DIR}/uploads/{user_id}")
        
        upload_dir.mkdir(parents=True, exist_ok=True)

        safe_filename = f"{uuid4()}_{os.path.basename(image_file.filename)}"
        stored_path = upload_dir / safe_filename

        contents = image_file.file.read()
        with stored_path.open("wb") as target_file:
            target_file.write(contents)

        image_record = Image(
            user_id=user_id,
            filename=image_file.filename,
            stored_path=str(stored_path),
            content_type=image_file.content_type,
        )
        db.add(image_record)
        db.flush()

        image = face_recognition.load_image_file(str(stored_path))
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        if not face_encodings:
            db.commit()
            db.refresh(image_record)
            return image_record

        existing_faces = db.query(Person).filter(Person.user_id == user_id).all()

        for face_location, face_encoding in zip(face_locations, face_encodings):
            best_match = self._match_face(
                existing_faces,
                face_encoding,
            )

            top, right, bottom, left = face_location

            # It's a new face, create a new person record and keep a cropped face image.
            if best_match is None:
                face_image_path = self._store_face_image(
                    source_image=image,
                    face_location=face_location,
                    user_id=user_id,
                )
                person_record = Person(
                    user_id=user_id,
                    face_image_path=face_image_path,
                    encoding=json.dumps(face_encoding.tolist()),
                )
                db.add(person_record)
                db.flush()
                
                person_image_record = PersonImage(
                    user_id=user_id,
                    person_id=person_record.id,
                    image_id=image_record.id,
                    top=top,
                    right=right,
                    bottom=bottom,
                    left=left
                )
                db.add(person_image_record)
                db.flush()
                
                existing_faces.append(person_record)
            else:
                person_id = best_match.id
                person_image_record = PersonImage(
                    user_id=user_id,
                    person_id=person_id,
                    image_id=image_record.id,
                    top=top,
                    right=right,
                    bottom=bottom,
                    left=left
                )
                db.add(person_image_record)
                db.flush()

        db.commit()
        db.refresh(image_record)
        return image_record

    def list_images(self, db: Session, user_id: int):
        return (
            db.query(Image)
            .filter(Image.user_id == user_id)
            .order_by(Image.created_at.desc())
            .all()
        )

    def get_image(self, db: Session, user_id: int, image_id: int):
        image = (
            db.query(Image)
            .filter(Image.id == image_id, Image.user_id == user_id)
            .first()
        )
        if image is None:
            raise HTTPException(status_code=404, detail="Image not found")
        return image

    def get_image_file(self, db: Session, user_id: int, image_id: int) -> Image:
        image = self.get_image(db, user_id, image_id)
        image_path = Path(image.stored_path)
        if not image_path.is_file():
            raise HTTPException(status_code=404, detail="Stored image file not found")
        return image

    def get_random_image(self, db: Session, user_id: int):
        image = (
            db.query(Image)
            .filter(Image.user_id == user_id)
            .order_by(func.random())
            .first()
        )
        if image is None:
            raise HTTPException(status_code=404, detail="No images found for user")

        commentary = image.commentary
        if not commentary:
            commentary = self._generate_commentary(image)
            image.commentary = commentary
            db.add(image)
            db.commit()
            db.refresh(image)

        return {
            "id": image.id,
            "filename": image.filename,
            "stored_path": image.stored_path,
            "content_type": image.content_type,
            "created_at": image.created_at,
            "commentary": image.commentary,
        }
  
    def _match_face(self, existing_faces: list[Person], face_encoding):
        if not existing_faces:
            return None

        best_face = None
        best_distance = None
        for face in existing_faces:
            known_encoding = json.loads(face.encoding)
            distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
            if distance <= settings.FACE_MATCH_TOLERANCE:
                if best_distance is None or distance < best_distance:
                    best_distance = distance
                    best_face = face

        return best_face

    def _store_face_image(self, source_image, face_location, user_id: int) -> str:
        top, right, bottom, left = face_location
        image_height, image_width = source_image.shape[:2]
        face_width = right - left
        face_height = bottom - top

        # Keep a little extra context around the face so the saved preview is usable.
        extra_left = int(face_width * 0.35)
        extra_right = int(face_width * 0.35)
        extra_top = int(face_height * 0.7)
        extra_bottom = int(face_height * 0.45)

        crop_left = max(0, left - extra_left)
        crop_right = min(image_width, right + extra_right)
        crop_top = max(0, top - extra_top)
        crop_bottom = min(image_height, bottom + extra_bottom)

        cropped_image = source_image[crop_top:crop_bottom, crop_left:crop_right]
        if cropped_image.size == 0:
            raise HTTPException(status_code=500, detail="Failed to crop face image")

        face_dir = Path(settings.STORAGE_DIR) / "faces" / str(user_id)
        face_dir.mkdir(parents=True, exist_ok=True)

        face_filename = f"{uuid4()}.png"
        face_path = face_dir / face_filename

        success = cv2.imwrite(
            str(face_path),
            cv2.cvtColor(cropped_image, cv2.COLOR_RGB2BGR),
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store face image")

        return str(face_path)

    def _generate_commentary(self, image: Image) -> str:
        self._validate_azure_openai_settings()

        image_path = Path(image.stored_path)
        if not image_path.exists():
            raise HTTPException(status_code=500, detail="Stored image file not found")

        mime_type = image.content_type or "application/octet-stream"
        image_bytes = image_path.read_bytes()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        endpoint = settings.AZURE_OPENAI_ENDPOINT.rstrip("/")
        deployment = settings.AZURE_OPENAI_DEPLOYMENT
        api_version = settings.AZURE_OPENAI_API_VERSION

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You write short, vivid commentary for personal photos. "
                                "Keep it to 2 sentences max, grounded in visible details, "
                                "and avoid claiming uncertain facts."
                            ),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this image with warm, concise commentary.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_b64}",
                            },
                        },
                    ],
                },
            ],
            "max_completion_tokens": 120,
        }

        req = request.Request(
            url=(
                f"{endpoint}/openai/deployments/{deployment}/chat/completions"
                f"?api-version={api_version}"
            ),
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "api-key": settings.AZURE_OPENAI_API_KEY,
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=30) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise HTTPException(
                status_code=502,
                detail=f"Azure OpenAI request failed: {detail or exc.reason}",
            ) from exc
        except error.URLError as exc:
            raise HTTPException(
                status_code=502,
                detail="Unable to reach Azure OpenAI service",
            ) from exc

        try:
            return response_payload["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, AttributeError) as exc:
            raise HTTPException(
                status_code=502,
                detail="Azure OpenAI returned an unexpected response",
            ) from exc

    def _validate_azure_openai_settings(self):
        missing_settings = [
            name
            for name, value in (
                ("AZURE_OPENAI_API_KEY", settings.AZURE_OPENAI_API_KEY),
                ("AZURE_OPENAI_ENDPOINT", settings.AZURE_OPENAI_ENDPOINT),
                ("AZURE_OPENAI_DEPLOYMENT", settings.AZURE_OPENAI_DEPLOYMENT),
            )
            if not value
        ]
        if missing_settings:
            raise HTTPException(
                status_code=500,
                detail=f"Missing Azure OpenAI settings: {', '.join(missing_settings)}",
            )

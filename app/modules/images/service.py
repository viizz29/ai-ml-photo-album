import base64
import json
import os
from pathlib import Path
from urllib import error, request
from uuid import uuid4

import face_recognition
from fastapi import HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings

from .model import Image
from app.modules.persons.model import Person
from app.modules.person_images.model import PersonImage


class ImagesService:
    def recognize_and_store(self, db: Session, image_file: UploadFile, user_id: int):
        if not image_file.filename:
            raise HTTPException(status_code=400, detail="Image filename is required")

        if not image_file.content_type or not image_file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image uploads are supported")

        upload_dir = Path(settings.FACE_IMAGE_UPLOAD_DIR)
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

        existing_faces = db.query(Person).all()

        for face_location, face_encoding in zip(face_locations, face_encodings):
            best_match = self._match_face(
                existing_faces,
                face_encoding,
            )
            
        
            # it's a new face, create a new person record, and new person_image record
            if best_match is None:
                top, right, bottom, left = face_location
                person_record = Person(
                    user_id=user_id,
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
                top, right, bottom, left = face_location
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

    def list_images(self, db: Session):
        return db.query(Image).order_by(Image.created_at.desc()).all()

    def get_image(self, db: Session, image_id: int):
        image = db.query(Image).filter(Image.id == image_id).first()
        if image is None:
            raise HTTPException(status_code=404, detail="Image not found")
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

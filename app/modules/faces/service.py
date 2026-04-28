import json
import os
from pathlib import Path
from uuid import uuid4

import face_recognition
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings

from .model import FaceImage, RecognizedFace


class FaceRecognitionService:
    def recognize_and_store(self, db: Session, image_file: UploadFile):
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

        image_record = FaceImage(
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
            return {"image": image_record, "matches": []}

        existing_faces = db.query(RecognizedFace).all()
        matches_by_face: list[dict] = []

        for face_location, face_encoding in zip(face_locations, face_encodings):
            person_id, matched_face_id, face_matches = self._match_face(
                existing_faces,
                face_encoding,
            )
            top, right, bottom, left = face_location
            face_record = RecognizedFace(
                image_id=image_record.id,
                person_id=person_id,
                encoding=json.dumps(face_encoding.tolist()),
                top=top,
                right=right,
                bottom=bottom,
                left=left,
                matched_face_id=matched_face_id,
            )
            db.add(face_record)
            db.flush()

            matches_by_face.append({"face_id": face_record.id, "matches": face_matches})
            existing_faces.append(face_record)

        db.commit()
        db.refresh(image_record)
        return {"image": image_record, "matches": matches_by_face}

    def list_images(self, db: Session):
        return db.query(FaceImage).order_by(FaceImage.created_at.desc()).all()

    def list_faces(self, db: Session):
        return db.query(RecognizedFace).order_by(RecognizedFace.created_at.desc()).all()

    def list_person_faces(self, db: Session, person_id: str):
        return (
            db.query(RecognizedFace)
            .filter(RecognizedFace.person_id == person_id)
            .order_by(RecognizedFace.created_at.desc())
            .all()
        )

    def _match_face(self, existing_faces: list[RecognizedFace], face_encoding):
        if not existing_faces:
            return str(uuid4()), None, []

        best_face = None
        best_distance = None
        matching_faces = []

        for face in existing_faces:
            known_encoding = json.loads(face.encoding)
            distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
            if distance <= settings.FACE_MATCH_TOLERANCE:
                matching_faces.append(
                    {
                        "matched_face_id": face.id,
                        "person_id": face.person_id,
                        "image_id": face.image_id,
                        "distance": round(float(distance), 4),
                    }
                )
                if best_distance is None or distance < best_distance:
                    best_distance = distance
                    best_face = face

        if best_face is None:
            return str(uuid4()), None, []

        matching_faces.sort(key=lambda item: item["distance"])
        return best_face.person_id, best_face.id, matching_faces

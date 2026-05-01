from fastapi import HTTPException
from sqlalchemy.orm import Session

from .model import Person

class PersonsService:
    def list_persons(self, db: Session, user_id: int):
        return db.query(Person).filter(Person.user_id == user_id).order_by(Person.created_at.desc()).all()

    def get_person(self, db: Session, user_id: int, person_id: int):
        person = db.query(Person).filter(Person.user_id == user_id, Person.id == person_id).first()
        if person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        return person

    def set_person_name(self, db: Session, user_id: int, person_id: int, name: str):
        person = (
            db.query(Person)
            .filter(Person.id == person_id, Person.user_id == user_id)
            .first()
        )
        if person is None:
            raise HTTPException(status_code=404, detail="Person not found")

        person.name = name
        db.commit()
        db.refresh(person)
        return person

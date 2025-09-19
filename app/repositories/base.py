from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List, Optional, Generic, TypeVar, Type


ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get(self, id: int) -> Optional[ModelType]:
        return self.session.get(self.model, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.session.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: dict) -> ModelType:
        obj = self.model(**obj_in)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        obj = self.get(id)
        if not obj:
            return None

        for key, value in obj_in.items():
            setattr(obj, key, value)

        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        obj = self.get(id)
        if not obj:
            return False

        self.session.delete(obj)
        self.session.commit()
        return True
    
    def find_one(self, filter_dict: dict) -> Optional[ModelType]:
        return self.session.scalars(select(self.model).filter_by(**filter_dict)).first()

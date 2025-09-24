from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional, Generic, TypeVar, Type


ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session

    def count(self) -> int:
        return self.session.query(self.model).count()

    def get(self, id: int) -> Optional[ModelType]:
        return self.session.get(self.model, id)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filter_by: Optional[Dict[str, Any]] = None,
        order_by: Optional[Dict[str, str]] = None
    ) -> List[ModelType]:
        model_columns = {column.name for column in self.model.__table__.columns}
        query = select(self.model)
        if filter_by:
            for key, value in filter_by.items():
                if key in model_columns:
                    if isinstance(value, list):
                        query = query.where(getattr(self.model, key).in_(value))
                    else:
                        query = query.where(getattr(self.model, key) == value)
        if order_by:
            for column, direction in order_by.items():
                if column in model_columns:
                    if direction.lower() == 'desc':
                        query = query.order_by(getattr(self.model, column).desc())
                    else:
                        query = query.order_by(getattr(self.model, column).asc())
        query = query.offset(skip).limit(limit)
        result = self.session.execute(query)
        return result.scalars().all()

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

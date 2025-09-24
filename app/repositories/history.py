from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.document import Document
from app.repositories.base import BaseRepository
from app.models.history import History

class HistoryRepository(BaseRepository[History]):
    def __init__(self, session: Session):
        super().__init__(History, session)

    def get_all_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        filter_by: Optional[Dict[str, Any]] = None,
        order_by: Optional[Dict[str, str]] = None,
    ) -> Tuple[List[History], int]:
        query = self.session.query(History).join(History.document)
        total = self.count()
        if filter_by:
            for key, value in filter_by.items():
                if key == "dia":
                    query = query.filter(Document.dia == value)
                    total = query.count()
                elif key == "number":
                    query = query.filter(Document.number == value)
                    total = query.count()
        if order_by:
            for field, direction in order_by.items():
                column = getattr(History, field, None) or getattr(Document, field, None)
                if column:
                    query = query.order_by(column.desc() if direction == "desc" else column.asc())
        return query.offset(skip).limit(limit).all(), total

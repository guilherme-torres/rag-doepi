from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.history import History

class HistoryRepository(BaseRepository[History]):
    def __init__(self, session: Session):
        super().__init__(History, session)

    def get_by_document_id(self, document_id: str) -> Optional[History]:
        return self.session.scalar(select(History).where(History.document_id == document_id))

from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.history import History

class HistoryRepository(BaseRepository[History]):
    def __init__(self, session: Session):
        super().__init__(History, session)

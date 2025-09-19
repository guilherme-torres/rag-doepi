from typing import List, Optional
from app.repositories.history import HistoryRepository
from app.schemas.history import HistoryCreate, HistoryResponse


class HistoryService:
    def __init__(self, history_repository: HistoryRepository):
        self.history_repository = history_repository

    def create_history(self, history: HistoryCreate):
        history = self.history_repository.create(history.model_dump())
        return HistoryResponse.model_validate(history)

    def list_history(self, skip: int = 0, limit: int = 100) -> List[HistoryResponse]:
        histories = self.history_repository.get_all(skip=skip, limit=limit)
        return [HistoryResponse.model_validate(history) for history in histories]

    def get_by_document_id(self, document_id: int) -> Optional[HistoryResponse]:
        history = self.history_repository.find_one({"document_id": document_id})
        if history is None:
            return None
        return HistoryResponse.model_validate(history)

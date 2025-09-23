from typing import List, Optional
from app.repositories.history import HistoryRepository
from app.schemas.history import HistoryCreate, HistoryResponse, HistoryResponsePaginated


class HistoryService:
    def __init__(self, history_repository: HistoryRepository):
        self.history_repository = history_repository

    def create_history(self, history: HistoryCreate):
        history = self.history_repository.create(history.model_dump())
        return HistoryResponse.model_validate(history)

    def list_history(self, skip: int = 0, limit: int = 100) -> HistoryResponsePaginated:
        histories = self.history_repository.get_all(skip=skip, limit=limit)
        total = self.history_repository.count()
        history_data = [HistoryResponse.model_validate(history) for history in histories]
        return HistoryResponsePaginated(
            total=total,
            limit=limit,
            skip=skip,
            data=history_data,
        )

    def find_history(self, filter_dict: dict) -> Optional[HistoryResponse]:
        history = self.history_repository.find_one(filter_dict)
        if history is None:
            return None
        return HistoryResponse.model_validate(history)

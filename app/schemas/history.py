from typing import List
from pydantic import BaseModel, ConfigDict, computed_field
from app.schemas.document import DocumentResponseHistory


class HistoryBase(BaseModel):
    document_id: int
    ai_response: str


class HistoryCreate(HistoryBase):
    pass


class HistoryResponse(HistoryBase):
    id: int
    document: DocumentResponseHistory

    @computed_field
    @property
    def ai_response_short(self) -> str:
        return self.ai_response[:100] + " ..." if len(self.ai_response) > 100 else self.ai_response

    model_config = ConfigDict(from_attributes=True)


class HistoryResponsePaginated(BaseModel):
    total: int
    limit: int
    skip: int
    data: List[HistoryResponse]
    
    model_config = ConfigDict(from_attributes=True)

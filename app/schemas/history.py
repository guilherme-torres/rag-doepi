from pydantic import BaseModel, ConfigDict


class HistoryBase(BaseModel):
    document_id: int
    ai_response: str


class HistoryCreate(HistoryBase):
    pass


class HistoryResponse(HistoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

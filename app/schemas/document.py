from datetime import date
from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    tipo: str
    ref: str
    dia: date
    number: int
    year: int
    text: str
    filename: str
    link: str


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

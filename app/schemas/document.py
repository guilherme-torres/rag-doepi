from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    text: str
    filename: str


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

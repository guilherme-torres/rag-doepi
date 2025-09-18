from typing import Optional
from pydantic import BaseModel


class RAGResponse(BaseModel):
    response: Optional[str]

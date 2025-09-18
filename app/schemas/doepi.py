from typing import List
from pydantic import BaseModel


class DOEPIResponse(BaseModel):
    tipo: str
    numero: int
    ano: int
    referencia: str
    link: str

class DOEPIResponseList(BaseModel):
    data: List[DOEPIResponse]

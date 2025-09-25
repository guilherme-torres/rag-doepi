from typing import List
from pydantic import BaseModel


class DOEPIResponse(BaseModel):
    tipo: str
    numero: int
    ano: int
    dia: str
    referencia: str
    link: str

class DOEPIResponseLabelValue(BaseModel):
    label: str
    value: str

class DOEPIResponseList(BaseModel):
    data: List[DOEPIResponse]

class DOEPIResponseLabelValueList(BaseModel):
    data: List[DOEPIResponseLabelValue]

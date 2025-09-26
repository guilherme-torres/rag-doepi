from fastapi import HTTPException


class ApplicationException(HTTPException):
    def __init__(self, status_code: int = 500, detail: str = "Erro interno da aplicação"):
        super().__init__(status_code=status_code, detail=detail)

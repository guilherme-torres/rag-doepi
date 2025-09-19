from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.document import Document

class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: Session):
        super().__init__(Document, session)

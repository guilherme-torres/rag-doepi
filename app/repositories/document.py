from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.document import Document

class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: Session):
        super().__init__(Document, session)

    def get_by_filename(self, filename: str) -> Optional[Document]:
        return self.session.scalar(select(Document).where(Document.filename == filename))

from typing import Optional
from app.repositories.document import DocumentRepository
from app.schemas.document import DocumentCreate, DocumentResponse


class DocumentService:
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository

    def get_by_filename(self, filename: str) -> Optional[DocumentResponse]:
        document = self.document_repository.find_one({"filename": filename})
        if document is None:
            return None
        return DocumentResponse.model_validate(document)
    
    def get_by_ref(self, ref: str) -> Optional[DocumentResponse]:
        document = self.document_repository.find_one({"ref": ref})
        if document is None:
            return None
        return DocumentResponse.model_validate(document)

    def create_document(self, document: DocumentCreate) -> DocumentResponse:
        document = self.document_repository.create(document.model_dump())
        return DocumentResponse.model_validate(document)

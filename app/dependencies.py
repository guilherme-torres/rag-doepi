from sqlalchemy.orm import Session
from fastapi import Depends
from app.repositories.document import DocumentRepository
from app.repositories.history import HistoryRepository
from app.services.document import DocumentService
from app.services.history import HistoryService
from app.services.rag import RAGService
from app.services.doepi import DOEPIService
from app.database.db import get_db_session


def get_document_repository(session: Session = Depends(get_db_session)):
    return DocumentRepository(session)

def get_history_repository(session: Session = Depends(get_db_session)):
    return HistoryRepository(session)

def get_document_service(document_repository: DocumentRepository = Depends(get_document_repository)):
    return DocumentService(document_repository)

def get_history_service(history_repository: HistoryRepository = Depends(get_history_repository)):
    return HistoryService(history_repository)

def get_rag_service():
    return RAGService()

def get_doepi_service(
    document_service: DocumentService = Depends(get_document_service),
    history_service: HistoryService = Depends(get_history_service),
    rag_service: RAGService = Depends(get_rag_service),
):
    return DOEPIService(
        document_service,
        history_service,
        rag_service
    )

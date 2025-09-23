from datetime import datetime
import os
from typing import List, Optional
import requests
from app.config import Config
from app.schemas.document import DocumentCreate
from app.schemas.doepi import DOEPIResponse
from app.schemas.history import HistoryCreate
from app.schemas.rag import RAGResponse
from app.services.document import DocumentService
from app.services.history import HistoryService
from app.services.rag import RAGService


class DOEPIService:
    def __init__(
        self,
        document_service: DocumentService,
        history_service: HistoryService,
        rag_service: RAGService
    ):
        self.config = Config()
        self.document_service = document_service
        self.history_service = history_service
        self.rag_service = rag_service

    def list_doe(self) -> List[DOEPIResponse]:
        try:
            response = requests.get(self.config.DOEPI_ENDPOINT)
            response.raise_for_status()
            list_doe = response.json()["dados"]
            return [DOEPIResponse(**doe) for doe in list_doe]
        except requests.exceptions.RequestException as e:
            print(f"Erro ao consultar API: {e}")
            raise

    def get_last_doe(self) -> DOEPIResponse:
        list_doe = self.list_doe()
        ultimo_doe = list_doe[0]
        return ultimo_doe

    def search_doe(self, ref: str) -> Optional[DOEPIResponse]:
        list_doe = self.list_doe()
        doe_found = [doe for doe in list_doe if doe.referencia == ref]
        if len(doe_found) == 0:
            return None
        return doe_found[0]
    
    def download_doe(self, doe: DOEPIResponse, chunk_size=8192) -> str:
        try:
            if not os.path.exists(self.config.DOWNLOAD_DIR):
                os.mkdir(self.config.DOWNLOAD_DIR)
            filename = f"DOEPI_{doe.numero}_{doe.ano}.pdf"
            file_path = os.path.join(self.config.DOWNLOAD_DIR, filename)
            print("baixando DOE...")
            response = requests.get(doe.link, stream=True)
            response.raise_for_status()
            with open(file_path, 'wb') as pdf_doe:
                for chunk in response.iter_content(chunk_size):
                    pdf_doe.write(chunk)
            return filename
        except requests.exceptions.RequestException as e:
            print(f"Erro ao baixar arquivo: {e}")
            raise
        except IOError as e:
            print(f"Erro ao salvar arquivo: {e}")
            raise

    def analyze_doe(self, doe: DOEPIResponse, model: str) -> RAGResponse:
        filename = self.download_doe(doe)
        document_exist = self.document_service.get_by_ref(doe.referencia)
        file_path = os.path.join(self.config.DOWNLOAD_DIR, filename)
        if document_exist:
            # apaga o arquivo baixado se o documento já foi salvo no BD
            if os.path.exists(file_path):
                os.remove(file_path)
            history_exist = self.history_service.find_history({
                "document_id": document_exist.id,
                "ai_model": model,
            })
            if history_exist:
                return RAGResponse(response=history_exist.ai_response)
            prompt = self.rag_service.make_rag_prompt(document_exist.text)
            ai_response = self.rag_service.generate_answer(model, prompt)
            self.history_service.create_history(HistoryCreate(
                document_id=document_exist.id,
                ai_response=ai_response,
                ai_model=model,
            ))
            return RAGResponse(response=ai_response)
            # return RAGResponse(response="resposta do modelo")
        
        pdf_text = self.rag_service.load_pdf(filename=filename)
        document = self.document_service.create_document(DocumentCreate(
            text=pdf_text,
            filename=filename,
            tipo=doe.tipo,
            ref=doe.referencia,
            dia=datetime.strptime(doe.dia, "%Y-%m-%d").date(),
            number=doe.numero,
            year=doe.ano,
            link=doe.link,
        ))
        # apaga o arquivo baixado após salvar o documento no BD
        if os.path.exists(file_path):
            os.remove(file_path)
        prompt = self.rag_service.make_rag_prompt(pdf_text)
        ai_response = self.rag_service.generate_answer(model, prompt)
        self.history_service.create_history(HistoryCreate(
            document_id=document.id,
            ai_response=ai_response,
            ai_model=model,
        ))
        return RAGResponse(response=ai_response)
        # return RAGResponse(response="resposta do modelo")

    def analyze_last_doe(self, model: str) -> RAGResponse:
        last_doe = self.get_last_doe()
        return self.analyze_doe(last_doe, model)

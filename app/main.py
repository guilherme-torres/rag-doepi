import os
import requests
import pandas as pd
from google import genai
from PyPDF2 import PdfReader
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.services.document import DocumentService
from app.services.history import HistoryService
from app.database.db import Base, engine
from app.dependencies import get_document_service, get_history_service
from app.schemas.document import DocumentCreate
from app.schemas.history import HistoryCreate, HistoryResponse
from app.config import Config

Base.metadata.create_all(engine)

download_dir = "temp"

def search_last_doe() -> dict:
    try:
        response = requests.get(Config().DOEPI_ENDPOINT)
        response.raise_for_status()
        ultimo_doe = response.json()["dados"][0]
        return ultimo_doe
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar arquivo: {e}")


def download_last_doe(chunk_size=8192) -> str:
    try:
        if not os.path.exists(download_dir):
            os.mkdir(download_dir)
        ultimo_doe = search_last_doe()
        filename = f"DOEPI_{ultimo_doe["numero"]}_{ultimo_doe["ano"]}.pdf"
        file_path = os.path.join(download_dir, filename)
        if os.path.exists(file_path):
            print(f"o último DOE já foi baixado: {filename}")
            return filename
        print("baixando último DOE...")
        response = requests.get(ultimo_doe["link"], stream=True)
        response.raise_for_status()
        with open(file_path, 'wb') as pdf_doe:
            for chunk in response.iter_content(chunk_size):
                pdf_doe.write(chunk)
        return filename
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar arquivo: {e}")
    except IOError as e:
        print(f"Erro ao salvar arquivo: {e}")


def load_pdf(filename: str) -> str:
    try:
        print(f"iniciando extração do texto de {filename}")
        raw_text = ""
        file_path = os.path.join(download_dir, filename)
        pdfreader = PdfReader(file_path)
        total_paginas = len(pdfreader.pages)
        for i, page in enumerate(pdfreader.pages[2:-1]):
            print(f"extraindo texto da página {i+1}/{total_paginas}")
            content = page.extract_text()
            if content:
                raw_text += content
        print("extração de texto concluída!")
        return raw_text
    except Exception as e:
        print(f"erro ao extrair texto do arquivo {filename}: {e}")


client = genai.Client(api_key=Config().GEMINI_API_KEY)

df = pd.read_csv(os.getenv("SHEETS_URL"))
atos_compilados = df["Nº da Lei/ Decreto"].values

def make_rag_prompt(text: str):
    prompt = f"""
Este Diário Oficial alterou algum dos atos compilados referidos na tabela? Se Sim, quais?

### Entrada:

**Lista de Atos Compilados:**
{"\n".join([f"- {ato_compilado}" for ato_compilado in atos_compilados])}

**Texto do Diário Oficial:**
```
{text}
```
    """
    return prompt


def generate_answer(prompt: str):
    result = client.models.generate_content(
        model=Config().AI_MODEL, contents=prompt
    )
    return result.text


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def root():
    return "pong"


@app.post("/fetch-last-doe")
def fetch_last_doe():
    return search_last_doe()


@app.post("/analyze-last-doe")
def analyze_last_doe(
    document_service: DocumentService = Depends(get_document_service),
    history_service: HistoryService = Depends(get_history_service),
):
    # filename = download_last_doe()
    filename = "DOEPI_120_2025.pdf"
    print("buscado documento no bd...")
    document_exist = document_service.get_by_filename(filename)
    if document_exist:
        print("documento encontrado!")
        print("buscando histórico no bd...")
        history_exist = history_service.get_by_document_id(document_exist.id)
        if history_exist:
            print("histórico encontrado!")
            return {"response": history_exist.ai_response}
        print("histórico não encontrado!")
        prompt = make_rag_prompt(document_exist.text)
        print(f"consultando o modelo: {Config().AI_MODEL}")
        ai_response = generate_answer(prompt)
        return {"response": ai_response}
    print("documento não encontrado!")
    
    pdf_text = load_pdf(filename=filename)
    print("salvando texto do documento no banco de dados...")
    document = document_service.create_document(DocumentCreate(
        text=pdf_text, filename=filename
    ))
    prompt = make_rag_prompt(pdf_text)
    print(f"consultando o modelo: {Config().AI_MODEL}")
    ai_response = generate_answer(prompt)
    print("salvando histórico da consulta no banco de dados...")
    history_service.create_history(HistoryCreate(
        document_id=document.id,
        ai_response=ai_response,
    ))
    return {"response": ai_response}

import os
import requests
import redis
from dotenv import load_dotenv
import pandas as pd
from google import genai
from PyPDF2 import PdfReader
from flask import Flask
from flask_cors import CORS


load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

download_dir = "temp"

def search_last_doe() -> dict:
    try:
        response = requests.get("https://www.diario.pi.gov.br/doe/mobile/listardoe.json")
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
        print("buscando texto do pdf em cache...")
        texto_em_cache = r.get(filename)
        if texto_em_cache:
            return texto_em_cache
        print(f"texto não encontrado em cache. Extraindo texto do pdf: {filename}")
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
        print("salvando texto do arquivo em cache...")
        r.set(filename, raw_text)
        return raw_text
    except Exception as e:
        print(f"erro ao extrair texto do arquivo {filename}: {e}")


client = genai.Client()

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
        model=os.getenv("AI_MODEL"), contents=prompt
    )
    return result.text


app = Flask(__name__)
CORS(app)

@app.route("/ping")
def root():
    return "pong"


@app.route("/fetch-last-doe", methods=["POST"])
def fetch_last_doe():
    return search_last_doe()


@app.route("/analyze-last-doe", methods=["POST"])
def analyze_last_doe():
    filename = download_last_doe()
    # filename = "DOEPI_120_2025.pdf"
    pdf_text = load_pdf(filename)
    prompt = make_rag_prompt(pdf_text)
    ai_response = generate_answer(prompt)
    return {"response": ai_response}

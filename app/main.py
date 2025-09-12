import os
import requests
import redis
from dotenv import load_dotenv
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
        print("texto não encontrado em cache. Extraindo texto do pdf...")
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

def make_rag_prompt(text: str):
    prompt = f"""
Você é um assistente jurídico especializado na análise de atos normativos. Receberá o texto do Diário Oficial do Estado do Piauí (DOEPI), que contém publicações oficiais do dia.

Sua tarefa é identificar **quais Leis, Decretos ou Portarias foram mencionadas como alteradas, revogadas ou regulamentadas no DOEPI**.

### Regras para análise:

* Considere como **alterado** qualquer ato que tenha sido **modificado, revogado total ou parcialmente, substituído ou regulamentado**.
* A alteração pode ocorrer de forma explícita ou implícita, como nos casos em que um novo ato menciona alterar, revogar ou regulamentar um anterior.
* Ignore republicações sem alterações, homenagens ou meras citações sem efeito normativo.
* Analise apenas **Leis**, **Decretos** e **Portarias**.

### Entrada:

**Texto do DOEPI:**
{text}

### Saída esperada (formato de resposta):

Liste apenas os atos que foram alterados, com breve justificativa extraída do DOEPI:

**Atos alterados encontrados no DOEPI:**

* **Decreto nº 10.123/2020** - Alterado pelo Decreto nº 10.987/2025.
* **Portaria nº 58/2023** - Revogada conforme publicação no DOEPI.
    """
    return prompt


def generate_answer(prompt: str):
    result = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
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
    pdf_text = load_pdf(filename)
    prompt = make_rag_prompt(pdf_text)
    ai_response = generate_answer(prompt)
    return {"response": ai_response}

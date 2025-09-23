import os
from typing import Optional
from PyPDF2 import PdfReader
from google import genai
import pandas as pd
from app.config import Config


class RAGService:
    def __init__(self):
        self.config = Config()
        self.client = genai.Client(api_key=self.config.GEMINI_API_KEY)

    def load_pdf(self, filename: str) -> str:
        try:
            print(f"iniciando extração do texto de {filename}")
            raw_text = ""
            file_path = os.path.join(self.config.DOWNLOAD_DIR, filename)
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

    def make_rag_prompt(self, text: str) -> str:
        df = pd.read_csv(self.config.SHEETS_URL)
        atos_compilados = df["Nº da Lei/ Decreto"].values
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
    
    def generate_answer(self, model: str, prompt: str) -> Optional[str]:
        result = self.client.models.generate_content(
            model=model, contents=prompt
        )
        return result.text

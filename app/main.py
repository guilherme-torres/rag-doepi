import json
from typing import List
from app.schemas.history import HistoryResponsePaginated
from app.services.history import HistoryService
import redis
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.rag import RAGResponse
from app.services.doepi import DOEPIService
from app.database.db import Base, engine
from app.dependencies import get_doepi_service, get_history_service
from app.schemas.doepi import DOEPIResponse, DOEPIResponseList
from app.config import Config

Base.metadata.create_all(engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

r = redis.Redis(
    host=Config().REDIS_HOST,
    port=Config().REDIS_PORT,
    password=Config().REDIS_PASSWORD,
    decode_responses=True
)

@app.get("/ping")
def root():
    return "pong"


@app.get("/doepi/last", response_model=DOEPIResponse)
def fetch_last_doe(doepi_service: DOEPIService = Depends(get_doepi_service)):
    return doepi_service.get_last_doe()


@app.post("/doepi/last/analyze", response_model=RAGResponse)
def analyze_last_doe(doepi_service: DOEPIService = Depends(get_doepi_service)):
    return doepi_service.analyze_last_doe()


@app.get("/doepi", response_model=DOEPIResponseList)
def list_doepi(doepi_service: DOEPIService = Depends(get_doepi_service)):
    list_doe_cache = r.get("list_doepi")
    if list_doe_cache:
        print("resposta recuperada do cache")
        list_doe_obj = json.loads(list_doe_cache)
        list_doe = [DOEPIResponse.model_validate(doe_obj) for doe_obj in list_doe_obj]
        return DOEPIResponseList(data=list_doe)
    print("resposta não encontrada no cache")
    list_doe = doepi_service.list_doe()
    list_doe_json_str = json.dumps([doe.model_dump() for doe in list_doe])
    # salva a resposta em cache por 12 horas
    r.set("list_doepi", list_doe_json_str, ex=43200)
    return DOEPIResponseList(data=list_doe)


@app.post("/doepi/analyze", response_model=RAGResponse)
def analyze_doe(ref: str, doepi_service: DOEPIService = Depends(get_doepi_service)):
    doe_cache = r.get(ref)
    if doe_cache:
        doe = DOEPIResponse.model_validate_json(doe_cache)
        result = doepi_service.analyze_doe(doe)
        return result
    doe = doepi_service.search_doe(ref)
    if doe is None:
        raise HTTPException(status_code=404, detail=f"DOE não encontrado: {ref}")
    r.set(ref, doe.model_dump_json())
    result = doepi_service.analyze_doe(doe)
    return result


@app.get("/history", response_model=HistoryResponsePaginated)
def list_history(
    limit: int = 10,
    skip: int = 0,
    history_service: HistoryService = Depends(get_history_service)
):
    return history_service.list_history(limit=limit, skip=skip)

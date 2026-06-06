from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.functions.model import load, predict


artifact: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    artifact.update(load())
    yield
    artifact.clear()


app = FastAPI(
    title="Motor Fault Classifier",
    version="1.0.0",
    description=(
        "API de inferencia para classificacao de falhas em motores industriais. "
        "Recebe leituras de sensores e retorna a classe de falha prevista "
        "com as respectivas probabilidades."
    ),
    lifespan=lifespan,
)


class SensorReading(BaseModel):
    rotacao_rpm: float = Field(gt=0, description="Rotacao do motor em RPM", examples=[1776.0])
    vibracao_mm_s: float = Field(gt=0, description="Vibracao em mm/s", examples=[2.7])
    temperatura_c: float = Field(gt=0, description="Temperatura em graus Celsius", examples=[68.5])
    corrente_a: float = Field(gt=0, description="Corrente eletrica em Amperes", examples=[12.3])


class PredictionResponse(BaseModel):
    falha: str = Field(description="Classe de falha prevista")
    probabilidades: dict[str, Any] = Field(description="Probabilidade por classe")

    model_config = {
        "json_schema_extra": {
            "example": {
                "falha": "Normal",
                "probabilidades": {
                    "Normal": 0.95,
                    "Desbalanceamento": 0.02,
                    "Superaquecimento": 0.02,
                    "Falha mecanica": 0.01,
                },
            }
        }
    }


@app.get("/health", summary="Health check", tags=["Status"])
def health():
    """Verifica se a API esta no ar e o modelo carregado."""
    return {"status": "ok"}


@app.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Classificar leitura de sensores",
    tags=["Inferencia"],
)
def predict_endpoint(reading: SensorReading):
    """
    Recebe uma leitura dos sensores do motor e retorna:

    - **falha**: classe prevista (`Normal`, `Desbalanceamento`, `Superaquecimento`, `Falha mecanica`)
    - **probabilidades**: probabilidade de cada classe
    """
    return predict(vars=reading.model_dump(), artifact=artifact)

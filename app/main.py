import logging

from fastapi import FastAPI

from app.configurations import EnvConfigs
from app.adapters.openai import OpenAIAdapter
from app.adapters.in_memory_repository import InMemoryTranscriptRepository
from app.services.transcript_service import TranscriptService
from app.api.routes import router, get_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)

app = FastAPI(title="Transcript Analysis API")

env = EnvConfigs()
llm = OpenAIAdapter(api_key=env.OPENAI_API_KEY, model=env.OPENAI_MODEL)
repository = InMemoryTranscriptRepository()
service = TranscriptService(llm=llm, repository=repository)

app.dependency_overrides[get_service] = lambda: service
app.include_router(router)

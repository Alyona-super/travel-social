from fastapi import FastAPI
from .api import router
from .database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Feed Service", description="Posts, comments, feed and geo search")

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "feed-service"}
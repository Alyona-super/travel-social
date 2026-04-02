from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
#from api import profile_router
from api.profile_router import profile_router
from database import engine, Base

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Profile Service",
    description="Service for managing user profiles",
    version="1.0.0"
)
# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Подключаем роутеры
app.include_router(profile_router, prefix="/api/v1/profile", tags=["profile"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "profile-service"}

@app.on_event("startup")
async def startup_event():
    logger.info("Profile service started")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Profile service stopped")
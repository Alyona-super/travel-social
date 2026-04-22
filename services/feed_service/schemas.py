from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# Посты
class PostCreate(BaseModel):
    title: Optional[str] = None
    content: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PostResponse(BaseModel):
    id: UUID
    author_id: UUID
    title: Optional[str]
    content: str
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# ---- Комментарии ----
class CommentCreate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: UUID
    post_id: UUID
    author_id: UUID
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

# Лента и геопоиск
class FeedQuery(BaseModel):
    skip: int = 0
    limit: int = 20

class NearbyQuery(BaseModel):
    lat: float
    lon: float
    radius_km: float = 5.0
    skip: int = 0
    limit: int = 20
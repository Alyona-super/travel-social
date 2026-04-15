from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# для создания пользователя
class UserCreate(BaseModel):

    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    favorite_categories: Optional[List[str]] = []

# для ответа с данными пользователя
class UserResponse(BaseModel):

    id: UUID
    email: EmailStr
    full_name: Optional[str]
    favorite_categories: Optional[List[str]]
    avatar_url: Optional[str]
    bio: Optional[str]
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

# для обновления пользователя
class UserUpdate(BaseModel):

    full_name: Optional[str] = None
    favorite_categories: Optional[List[str]] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

#  для входа
class LoginRequest(BaseModel):

    email: EmailStr
    password: str

#  для ответа с токеном
class TokenResponse(BaseModel):

    access_token: str
    token_type: str = "bearer"
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from database import get_db
from models import User
from schemas import UserCreate, UserResponse, UserUpdate, LoginRequest, TokenResponse
from auth import get_password_hash, verify_password, create_access_token, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# регистрация нового пользователя
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):

    # Проверяем, существует ли пользователь
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Создаем нового
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        favorite_categories=user_data.favorite_categories
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"New user registered: {new_user.email}")
    return new_user

#вход в систему
@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # Ищем пользователя
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Проверяем пароль
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Создаем токен
    access_token = create_access_token(data={"sub": str(user.id)})

    logger.info(f"User logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    #получение своего профиля
    user_id = current_user["user_id"]
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
        user_update: UserUpdate,
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    #обновление своего профиля
    user_id = current_user["user_id"]
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Обновляем только переданные поля
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.favorite_categories is not None:
        user.favorite_categories = user_update.favorite_categories
    if user_update.avatar_url is not None:
        user.avatar_url = user_update.avatar_url
    if user_update.bio is not None:
        user.bio = user_update.bio

    db.commit()
    db.refresh(user)

    logger.info(f"User updated: {user.email}")
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(
        user_id: str,
        db: Session = Depends(get_db)
):
    #получение публичного профиля пользователя по ID
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
import math
from .database import get_db
from .models import Post, Comment
from .schemas import (
    PostCreate,
    PostUpdate,
    PostResponse,
    CommentCreate,
    CommentResponse,
)
from .auth import get_current_user

router = APIRouter(prefix="/api/v1", tags=["posts", "feed", "comments"])


# Посты
@router.post("/posts", response_model=PostResponse, status_code=201)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    new_post = Post(
        author_id=current_user["user_id"],
        title=post_data.title,
        content=post_data.content,
        latitude=post_data.latitude,
        longitude=post_data.longitude,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/posts/{post_id}", response_model=PostResponse)
def update_post(
    post_id: str,
    post_update: PostUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if str(post.author_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your post")
    for field, value in post_update.dict(exclude_unset=True).items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return post


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if str(post.author_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your post")
    db.delete(post)
    db.commit()
    return {"ok": True}


# Комментарии
@router.post(
    "/posts/{post_id}/comments", response_model=CommentResponse, status_code=201
)
def create_comment(
    post_id: str,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comment = Comment(
        post_id=post_id, author_id=current_user["user_id"], content=comment_data.content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
def get_comments(
    post_id: str, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    comments = (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return comments


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if str(comment.author_id) != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your comment")
    db.delete(comment)
    db.commit()
    return {"ok": True}


# ---- Лента новостей (хронологическая) ----
@router.get("/feed", response_model=List[PostResponse])
def get_feed(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    posts = (
        db.query(Post).order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    )
    return posts


# Поиск мест рядом (геолокация)
def haversine(lat1, lon1, lat2, lon2):
    # Радиус Земли в км
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return R * c


@router.get("/posts/nearby", response_model=List[PostResponse])
def get_nearby_posts(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(5.0),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    # Фильтр по квадрату для ускорения
    # 1 градус широты ≈ 111 км, долготы зависит от широты
    delta_lat = radius_km / 111.0
    delta_lon = radius_km / (111.0 * math.cos(math.radians(lat)))
    min_lat = lat - delta_lat
    max_lat = lat + delta_lat
    min_lon = lon - delta_lon
    max_lon = lon + delta_lon

    posts_in_box = (
        db.query(Post)
        .filter(
            Post.latitude.between(min_lat, max_lat),
            Post.longitude.between(min_lon, max_lon),
        )
        .all()
    )

    # Точная фильтрация по расстаянию
    result = []
    for post in posts_in_box:
        if post.latitude is not None and post.longitude is not None:
            dist = haversine(lat, lon, post.latitude, post.longitude)
            if dist <= radius_km:
                result.append(post)
    # Пагинация после фильтрации
    result = result[skip : skip + limit]
    return result

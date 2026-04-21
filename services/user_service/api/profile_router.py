from fastapi import APIRouter

profile_router = APIRouter()


@profile_router.get("/")
def get_profile():
    return {"message": "Profile works", "status": "ok"}


@profile_router.get("/health")
def health_check():
    return {"status": "alive"}

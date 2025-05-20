from fastapi import APIRouter

from .writing import router as writing_router

router = APIRouter()

router.include_router(writing_router, prefix="/writing")

from fastapi import APIRouter

from .writing import router as writing_router
from .reading import router as reading_router
from .quizzes import router as quizzes_router

router = APIRouter()

router.include_router(writing_router, prefix="/writing")
router.include_router(reading_router, prefix="/reading")
router.include_router(quizzes_router, prefix="/quizzes")

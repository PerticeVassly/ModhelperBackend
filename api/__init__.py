from .auth import router as auth_router
from .question import router as question_router

__all__ = [
    auth_router,
    question_router,
]

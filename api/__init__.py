from .auth import router as auth_router
from .question import router as question_router
from .mod import router as mod_router

__all__ = [
    auth_router,
    question_router,
    mod_router,
]

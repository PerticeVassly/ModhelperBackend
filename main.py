import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# import routers
from api import auth_router
from api import question_router

# import config
from config import settings, setup_logging

app= FastAPI()

logging.getLogger("watchfiles").setLevel(logging.WARNING)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(question_router)
app.include_router(auth_router)

setup_logging()

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
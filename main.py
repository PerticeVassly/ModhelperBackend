import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# import routers
from services import ask_router

# import config
from config import settings

app= FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    ask_router,prefix="/api",tags=["ask"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
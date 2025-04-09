from model import RegisterRequest, LoginRequest
from service import handle_register, handle_login
from fastapi import APIRouter

router = APIRouter()

@router.post("/register")
def register(user: RegisterRequest):
    response = handle_register(user)
    return response

@router.post("/login")
def login(user: LoginRequest):
    response = handle_login(user)
    return response
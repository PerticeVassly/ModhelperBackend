from model import UserRegister, UserLogin
from service import handle_register, handle_login
from fastapi import APIRouter

router = APIRouter()

@router.post("/register")
def register(user: UserRegister):
    response = handle_register(user)
    return response

@router.post("/login")
def login(user: UserLogin):
    response = handle_login(user)
    return response
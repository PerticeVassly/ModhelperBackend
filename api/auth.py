from model import RegisterRequest, LoginRequest
from service import handle_register, handle_login, handle_guest_login
from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/register")
def register(request: RegisterRequest):
    response = handle_register(request)
    return response

@router.post("/login")
def login(request: LoginRequest, raw_request: Request):
    response = None;
    if (raw_request.query_params.get("key") == "guest"):
        # Handle guest login
        response = handle_guest_login()
    else:
        response = handle_login(request)
    return response
from http.client import responses

from model import *
from service import *
from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/register", response_model = RegisterResponse)
def register(request: RegisterRequest):
    response = handle_register(request)
    return response

@router.post("/login", response_model = LoginResponse)
def login(request: LoginRequest, raw_request: Request):
    response = None;
    if (raw_request.query_params.get("key") == "guest"):
        response = handle_guest_login()
    else:
        response = handle_login(request)
    return response

@router.get("/user-info", response_model = UserInfoResponse)
def get_user_info(userInfo: UserInfo = Depends(get_current_user)):
    response = handle_get_user_info(userInfo)
    return response
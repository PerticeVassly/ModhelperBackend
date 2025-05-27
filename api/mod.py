from model import *
from service import *
from fastapi import APIRouter

router = APIRouter(prefix="/mod")

@router.get("/list", response_model = GetModResponse)
def get_mods(userInfo: UserInfo = Depends(get_current_user)) -> GetModResponse:
    response = handle_get_mods(userInfo)
    return response

@router.post("/add", response_model = AddModResponse)
def add_mod(mod: Mod) -> AddModResponse:
    response = handle_add_mod(mod)
    return response

@router.delete("/delete/{mod_id}", response_model = DeleteModResponse)
def delete_mod(mod_id: str) -> DeleteModResponse:
    response = handle_delete_mod(mod_id)
    return response


@router.post("/favorite/{mod_id}", response_model = ToggleFavoriteModResponse)
def toggle_favorite_mod(mod_id: str, userInfo: UserInfo = Depends(get_current_user)) -> ToggleFavoriteModResponse:
    response = handle_toggle_favorite_mod(mod_id, userInfo)
    return response


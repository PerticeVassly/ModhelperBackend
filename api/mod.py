from model import *
from service import *
from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/mod")

@router.get("/list", response_model = GetModResponse)
def get_mods(page: int, page_size: int,
             platform: Optional[str] = None,
             min_stars: int = 0,
             excluded_tags: Optional[str] = None,
             userInfo: UserInfo = Depends(get_current_user)) -> GetModResponse:
    excluded_tags_list = [t.strip() for t in excluded_tags.split(",") if t.strip()] if excluded_tags else None
    response = handle_get_mods(userInfo, page, page_size,
                                platform=platform,
                                min_stars=min_stars,
                                excluded_tags=excluded_tags_list)
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


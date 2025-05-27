from fastapi import HTTPException
from model import *
from db import metaInfosRepository, usersRepository, all_mod_names
import logging


logger = logging.getLogger("service")

def handle_get_mods(userInfo: UserInfo) -> GetModResponse:
    mods = metaInfosRepository.find_all_mod_vo()
    favorite_mod_ids = set(userInfo.favorite_mods)
    for mod in mods:
        if mod.id in favorite_mod_ids:
            mod.isFavorite = True
    return GetModResponse(mods=mods)

def handle_add_mod(mod: Mod) -> AddModResponse:
    if mod.mod_name in all_mod_names:
        raise HTTPException(status_code=400, detail="Mod already exists")

    result = metaInfosRepository.insert_one(mod)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to add mod")

    all_mod_names.append(mod.mod_name)

    logger.info(f"Mod {mod.mod_name} added successfully")
    return AddModResponse(message="Mod added successfully")

def handle_delete_mod(mod_id: str) -> DeleteModResponse:
    if not metaInfosRepository.exists_by_id(mod_id):
        logger.info(mod_id)
        raise HTTPException(status_code=404, detail=f"Mod not found{mod_id}")

    mod_name = metaInfosRepository.delete_mod_by_id(mod_id)
    if not mod_name:
        raise HTTPException(status_code=500, detail="Failed to delete mod")

    if mod_name in all_mod_names:
        all_mod_names.remove(mod_name)

    logger.info(f"Mod with ID {mod_id} deleted successfully")
    return DeleteModResponse(message="Mod deleted successfully")

def handle_toggle_favorite_mod(mod_id: str, userInfo: UserInfo) -> ToggleFavoriteModResponse:
    if not metaInfosRepository.exists_by_id(mod_id):
        raise HTTPException(status_code=404, detail="Mod not found")

    message = usersRepository.toggle_favorite_mod(userInfo.id, mod_id)
    if not message:
        raise HTTPException(status_code=500, detail="Failed to toggle favorite mod")
    return ToggleFavoriteModResponse(message=message)

from fastapi import HTTPException
from model import *
from db import metaInfosRepository, usersRepository, vectorDB
import db.global_vars as global_vars
import logging


logger = logging.getLogger("service")

def handle_get_mods(userInfo: UserInfo, page: int = 1, page_size: int = 20) -> GetModResponse:
    mods = metaInfosRepository.find_mod_by_page(page, page_size)
    favorite_mod_ids = set(userInfo.favorite_mods)
    for mod in mods:
        if mod.id in favorite_mod_ids:
            mod.isFavorite = True
    return GetModResponse(mods=mods)

def handle_add_mod(mod: Mod) -> AddModResponse:
    if mod.mod_name in global_vars.all_mod_names:
        raise HTTPException(status_code=400, detail="Mod already exists")

    result = metaInfosRepository.insert_one(mod)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to add mod")
    global_vars.refresh_all_names()

    vectorDB.add(
        raw_text=mod["introduction"],
        metadata=DocumentMetadata(
            document_name=mod["mod_name"] + " introduction",
            url=mod["detail_page_url"],
            type=DocumentEnum.introduction,
            mod_name=mod["mod_name"],
        ),
        overwrite=True
    )
    for guide in mod["guides"]:
        vectorDB.add(
            raw_text=guide["content"],
            metadata=DocumentMetadata(
                document_name=guide["guide_name"],
                url=guide["guide_page_url"],
                type=DocumentEnum.guide,
                mod_name=mod["mod_name"],
            ),
            overwrite=True
        )
    logger.info(f"Mod {mod.mod_name} added successfully")
    return AddModResponse(message="Mod added successfully")

def handle_delete_mod(mod_id: str) -> DeleteModResponse:
    mod = metaInfosRepository.find_by_id(mod_id)
    if not mod:
        raise HTTPException(status_code=404, detail=f"Mod not found{mod_id}")
    mod_name = metaInfosRepository.delete_mod_by_id(mod_id)
    if not mod_name:
        raise HTTPException(status_code=500, detail="Failed to delete mod")
    global_vars.refresh_all_names()

    res = vectorDB.delete_by_mod(mod.mod_name)
    if not res:
        raise HTTPException(status_code=500, detail="Failed to delete mod documents from vectorDB")

    logger.info(f"Mod with ID {mod_id} deleted successfully")
    return DeleteModResponse(message="Mod deleted successfully")

def handle_toggle_favorite_mod(mod_id: str, userInfo: UserInfo) -> ToggleFavoriteModResponse:
    if not metaInfosRepository.exists_by_id(mod_id):
        raise HTTPException(status_code=404, detail="Mod not found")

    message = usersRepository.toggle_favorite_mod(userInfo.id, mod_id)
    if not message:
        raise HTTPException(status_code=500, detail="Failed to toggle favorite mod")
    return ToggleFavoriteModResponse(message=message)

import json
from db import *
import sys
import os
from model import *
import json
import logging

blocked_documents = json.load(open("./scripts/blocked_documents.json"))

logger = logging.getLogger("database")


def filter_documents(raw_text: str) -> bool:
    # if the document is too long, we assume it as not relavant
    # TODO now do not need
    return True

def load_mods(overwrite: bool = False):
    # load all the json file in data/raw/

    # and add them to the database
    for file in os.listdir("./data/raw/"):
        if file.endswith(".json"):
            with open(f"./data/raw/{file}") as f:
                data = json.load(f)
                vectorDB.add(
                    raw_text= data["introduction"],
                    metadata= DocumentMetadata(
                        document_name= data["mod_name"] + " introduction",
                        url= data["detail_page_url"],
                        type= DocumentEnum.introduction,
                        mod_name= data["mod_name"],
                    ),
                    overwrite=overwrite
                )

                tobe_blocked_documents = set(blocked_documents.get(data["mod_name"], []))
                for guide in data["guides"]:
                    if guide["guide_name"] in tobe_blocked_documents:
                        logger.info(f"Blocked document: {guide['guide_name']}") 
                        continue
                    if not filter_documents(guide["content"]):
                        logger.info(f"Filtered document: {guide['guide_name']}")
                        continue
                    vectorDB.add(
                        raw_text= guide["content"],
                        metadata= DocumentMetadata(
                            document_name= guide["guide_name"],
                            url= guide["guide_page_url"],
                            type= DocumentEnum.guide,
                            mod_name= data["mod_name"],
                        ),
                        overwrite=overwrite
                    )
                    
                metaInfosRepository.insert_one(Mod.model_validate(data), overwrite=overwrite)
                    
                # for front in data["run_methods"]:
                #     graphDB.add(ModRelation(
                #         source_mod= data["mod_name"],
                #         target_mod= front,
                #         relationship_type= ModRelationType.dependency
                #     ))
                              
def str2platform(a: str) -> ModPlatform:
    a = a.strip().lower()
    if a.startswith("java"):
        return ModPlatform.JAVA
    elif a.startswith("bedrock"):
        return ModPlatform.BEDROCK
    else:
        return ModPlatform.CROSS

if __name__ == "__main__":    
    load_mods(overwrite = True)
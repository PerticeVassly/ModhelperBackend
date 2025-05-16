import json
from db import *
import sys
import os
from model import *

# def load_guide():
#     with open(f"./data/raw/{tag}/guide_page.json") as file:
#         file = json.load(file)
        
#         for mod in file:
#             mod_name = mod["mod_name"]
            
#             for guide in mod["guide_pages"]:
#                 guide_name = f"{mod_name} {guide['guide_name']}"
#                 guide_content = f"{guide_name}: {guide['guide_body']}"

#                 vectorDB.add(guide_name, guide_content)
        

# def load_detail():
#     with open(f"./data/raw/{tag}/detail_page.json") as file:
#         file = json.load(file)
        
#         for mod in file:
#             mod_name = mod["mod_name"]
#             mod_desc = mod["detail_page"]["mod_description"]
#             sup_plat = [str2platform(s) for s in mod["detail_page"]["support_platforms"]]
#             dep_meth = mod["detail_page"]["run_methods"]
#             mod_tags = mod["detail_page"]["mod_tags"]

#             relationDB.add(ModMetadata(
#                 mod_name,
#                 mod_tags,
#                 mod_desc,
#                 sup_plat[0],
#                 None
#             ))
            
#             for front in dep_meth:
#                 graphDB.add(ModRelation(
#                     mod_name,
#                     front,
#                     ModRelationType.dependency
#                 ))
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

                for guide in data["guides"]:
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
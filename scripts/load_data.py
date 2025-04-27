import json
from db import *
import sys

tag = ""

def load_guide():
    with open(f"./data/raw/{tag}/guide_page.json") as file:
        file = json.load(file)
        
        for mod in file:
            mod_name = mod["mod_name"]
            
            for guide in mod["guide_pages"]:
                guide_name = f"{mod_name} {guide['guide_name']}"
                guide_content = f"{guide_name}: {guide['guide_body']}"

                vectorDB.add(guide_name, guide_content)
        

def load_detail():
    with open(f"./data/raw/{tag}/detail_page.json") as file:
        file = json.load(file)
        
        for mod in file:
            mod_name = mod["mod_name"]
            mod_desc = mod["detail_page"]["mod_description"]
            sup_plat = [str2platform(s) for s in mod["detail_page"]["support_platforms"]]
            dep_meth = mod["detail_page"]["run_methods"]
            mod_tags = mod["detail_page"]["mod_tags"]

            relationDB.add(ModMetadata(
                mod_name,
                mod_tags,
                mod_desc,
                sup_plat[0],
                None
            ))
            
            for front in dep_meth:
                graphDB.add(ModRelation(
                    mod_name,
                    front,
                    ModRelationType.dependency
                ))

def str2platform(a: str) -> ModPlatform:
    a = a.strip().lower()
    if a.startswith("java"):
        return ModPlatform.JAVA
    elif a.startswith("bedrock"):
        return ModPlatform.BEDROCK
    else:
        return ModPlatform.CROSS

if __name__ == "__main__":    
    if len(sys.argv) > 1:
        tag = sys.argv[1]
    else:
        tag = "base"
    load_guide()
    load_detail()
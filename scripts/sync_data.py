# copy all the json files from crawler/data/mod to data/raw
import os

SRC_DIR = "../crawler/data/mod" # your src dir

def sync():
    # load all the json file in data/raw/
    # and add them to the database
    for file in os.listdir(SRC_DIR):
        if file.endswith(".json"):
            os.system(f"cp '{SRC_DIR}/{file}' ./data/raw/")
            print(f"copied {file} to data/raw")

if __name__ == "__main__":
    sync()
from pymongo import MongoClient
from config import settings
from model import UserInfo, ConversationInfo, MessageInfo, Mod
from bson import ObjectId
import logging
from pymongo.results import InsertOneResult


client = MongoClient(settings.MONGO_URL, serverSelectionTimeoutMS=3000)
client.admin.command('ping')
db = client["modhelper"]

logger = logging.getLogger("database")

class UsersCollection:
    def __init__(self):
        self.collection = db["users"]

    def find_one(self, user_id: ObjectId) -> UserInfo:
        user = self.collection.find_one({"_id": user_id})
        if user:
            return UserInfo(**user)
        return None

    def find_one_by_username(self, username : str) -> UserInfo:
        user = self.collection.find_one({"username": username})
        if user:
            return UserInfo(**user)
        return None
    
    def insert_one(self, user: UserInfo) -> InsertOneResult:
        try:
            # replace id into _id
            tmp = user.model_dump()
            tmp.pop("id")
            ans = self.collection.insert_one(tmp)
            return ans
        except Exception as e:
            logger.error(f"Error inserting user: {e}")
            return None

class ConversationsCollection:
    def __init__(self):
        self.collection = db["conversations"]
    
    def find_one(self, conversation_id: ObjectId) -> ConversationInfo:
        conversation = self.collection.find_one({"_id": conversation_id})
        if conversation:
            return ConversationInfo(**conversation)
        return None
    
    def delete_one(self, conversation_id: ObjectId) -> None:
            self.collection.delete_one({"_id": conversation_id})

    def update_ones_title(self, conversation_id : ObjectId, new_title : str) -> None:
        self.collection.update_one(
            {"_id": conversation_id},
            {"$set": {"title": new_title}}
        )
        logger.info(f"Conversation {conversation_id} updated to {new_title}")

    def find_all_by_user_id(self, user_id: ObjectId) -> list[ConversationInfo]:
        conversations = self.collection.find({"user_id": user_id})
        return [ConversationInfo(**conversation) for conversation in conversations]
    
    def insert_one(self, conversation: ConversationInfo) -> InsertOneResult:
        try:
            tmp = conversation.model_dump()
            tmp.pop("id")
            return self.collection.insert_one(tmp)
        except Exception as e:
            logger.error(f"Error inserting conversation: {e}")
            return None

class MessagesCollection:
    def __init__(self):
        self.collection = db["messages"]

    def delete_many_by_conversation_id(self, conversation_id: ObjectId) -> None:
        self.collection.delete_many({"conversation_id": conversation_id})
    
    def find_all_by_conversation_id(self, conversation_id: ObjectId) -> list[MessageInfo]:
        messages = self.collection.find({"conversation_id": conversation_id}).sort([("timestamp", 1)])
        return [MessageInfo(**message) for message in messages]

    def insert_one(self, message: MessageInfo) -> bool:
        try:
            tmp = message.model_dump()
            tmp.pop("id")
            self.collection.insert_one(tmp)
            return True
        except Exception as e:
            logger.error(f"Error inserting message: {e}")
            return False
        
class MetaInfoCollection:
    def __init__(self):
        self.collection = db["metaInfos"]
    
    def insert_one(self, mod : Mod, overwrite=False) -> bool:
        query = {"name" : mod.mod_name}
        existing = self.collection.find_one(query)
        if existing:
            if not overwrite:
                return False
            else:
                self.collection.replace_one(query, mod.model_dump())
                return True
        else:
            self.collection.insert_one(mod.model_dump())

    def find_all_mod_names(self):
        mods = self.collection.find({}, {"mod_name": 1, "_id": 0})
        return [mod["mod_name"] for mod in mods if "mod_name" in mod]
    
    def find_all_item_names(self):
        mods = self.collection.find({}, {"items.name": 1, "_id": 0})
        item_names = []
        for mod in mods:
            for item in mod.get("items", []):
                if "name" in item:
                    item_names.append(item["name"])
        return item_names
    
    def find_item_by_name(self, name: str) -> dict:
        item = self.collection.find_one({"items.name": name}, {"items.$": 1})
        if item and "items" in item:
            return item["items"][0]
        return None
    
    def find_all_biome_names(self):
        mods = self.collection.find({}, {"biomes.name": 1, "_id": 0})
        biome_names = []
        for mod in mods:
            for biome in mod.get("biomes", []):
                if "name" in biome:
                    biome_names.append(biome["name"])
        return biome_names
    
    def find_biome_by_name(self, name: str):
        biome = self.collection.find_one({"biomes.name": name}, {"biomes.$": 1})
        if biome and "biomes" in biome:
            return biome["biomes"][0]
        return None
    
    def find_all_entity_names(self):
        mods = self.collection.find({}, {"entities.name": 1, "_id": 0})
        entity_names = []
        for mod in mods:
            for entity in mod.get("entities", []):
                if "name" in entity:
                    entity_names.append(entity["name"])
        return entity_names
    
    def find_entity_by_name(self, name: str):
        entity = self.collection.find_one({"entities.name": name}, {"entities.$": 1})
        if entity and "entities" in entity:
            return entity["entities"][0]
        return None
    
    def find_all_structure_names(self):
        mods = self.collection.find({}, {"structures.name": 1, "_id": 0})
        structure_names = []
        for mod in mods:
            for structure in mod.get("structures", []):
                if "name" in structure:
                    structure_names.append(structure["name"])
        return structure_names
    
    def find_structure_by_name(self, name: str):
        structure = self.collection.find_one({"structures.name": name}, {"structures.$": 1})
        if structure and "structures" in structure:
            return structure["structures"][0]
        return None 

usersRepository = UsersCollection()
conversationsRepository = ConversationsCollection()
messagesRepository = MessagesCollection()
metaInfosRepository = MetaInfoCollection()



from pymongo import MongoClient
from config import settings
from model import *
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

    def toggle_favorite_mod(self, user_id: ObjectId, mod_id: str) -> str | None:
        user = self.find_one(user_id)
        if not user:
            logger.error(f"用户 {user_id} 未找到")
            return None
        if mod_id in user.favorite_mods:
            result = self.collection.update_one(
                {"_id": user_id},
                {"$pull": {"favorite_mods": mod_id}}
            )
            if result.modified_count > 0:
                return "Removed from favorites"
        else:
            result = self.collection.update_one(
                {"_id": user_id},
                {"$addToSet": {"favorite_mods": mod_id}}
            )
            if result.modified_count > 0:
                return "Added to favorites"
        logger.error("Failed to toggle favorite mod")
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
            return True

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
    
    def find_item_by_name(self, name: str) -> tuple[GeneralItem, str]:
        doc = self.collection.find_one({"items.name": name})
        if doc and "items" in doc:
            for item in doc["items"]:
                if item.get("name") == name:
                    return GeneralItem.model_validate(item), doc["mod_name"]
        return None, None
        
    
    def find_all_biome_names(self):
        mods = self.collection.find({}, {"biomes.name": 1, "_id": 0})
        biome_names = []
        for mod in mods:
            for biome in mod.get("biomes", []):
                if "name" in biome:
                    biome_names.append(biome["name"])
        return biome_names
    
    def find_biome_by_name(self, name: str) -> GeneralItem:
        doc = self.collection.find_one({"biomes.name": name})
        if doc and "biomes" in doc:
            for biome in doc["biomes"]:
                if biome.get("name") == name:
                    return GeneralItem.model_validate(biome), doc["mod_name"]
        return None
    
    def find_all_entity_names(self):
        mods = self.collection.find({}, {"entities.name": 1, "_id": 0})
        entity_names = []
        for mod in mods:
            for entity in mod.get("entities", []):
                if "name" in entity:
                    entity_names.append(entity["name"])
        return entity_names
    
    def find_entity_by_name(self, name: str) -> GeneralItem:
        doc = self.collection.find_one({"entities.name": name})
        if doc and "entities" in doc:
            for entity in doc["entities"]:
                if entity.get("name") == name:
                    return GeneralItem.model_validate(entity), doc["mod_name"]
        return None
    
    def find_all_structure_names(self):
        mods = self.collection.find({}, {"structures.name": 1, "_id": 0})
        structure_names = []
        for mod in mods:
            for structure in mod.get("structures", []):
                if "name" in structure:
                    structure_names.append(structure["name"])
        return structure_names
    
    def find_structure_by_name(self, name: str) -> GeneralItem:
        doc = self.collection.find_one({"structures.name": name})
        if doc and "structures" in doc:
            for structure in doc["structures"]:
                if structure.get("name") == name:
                    return GeneralItem.model_validate(structure), doc["mod_name"]
        return None

    def find_full_document_by_metadata(self, metadata: DocumentMetadata) -> str:
        if metadata.type == DocumentEnum.introduction:
            mod_name = metadata.mod_name
            # find the introduction of the mod
            introductions = self.collection.find_one({"mod_name": mod_name}, {"introduction": 1})
            return introductions["introduction"] if introductions else None
        elif metadata.type == DocumentEnum.guide:
            mod_name = metadata.mod_name
            guide_name = metadata.document_name
            # find the guide of the mod
            guides = self.collection.find_one({"mod_name": mod_name, "guides.guide_name": guide_name}, {"guides.$": 1})
            return guides["guides"][0]["content"] if guides else None
        else:
            logger.error(f"Unknown document type: {metadata.type}")
            return None

    def filter_mods(self, categories: list[str] = None) -> list[ModBriefIntroduction]:
        query = {"categories": {"$in": categories}} if categories else {}
        projection = {"mod_name": 1, "detail_page_url": 1, "introduction": 1, "categories": 1}
        mods = list(self.collection.find(query, projection))

        if categories:
            category_set = set(categories)
            def match_score(mod):
                return len(set(mod.get("categories", [])) & category_set)
            mods.sort(key=match_score, reverse=True)

        return [ModBriefIntroduction(**mod) for mod in mods]

    def find_all_mod_vo(self) -> list[ModVO]:
        mods = self.collection.find({})
        result = []
        for mod in mods:
            mod_vo_dict = mod.copy()
            mod_vo_dict["id"] = str(mod_vo_dict.pop("_id"))
            mod_vo_dict["isFavorite"] = False
            result.append(ModVO.model_validate(mod_vo_dict))
        return result

    def delete_mod_by_id(self, mod_id: str) -> str | None:
        try:
            mod = self.collection.find_one({"_id": ObjectId(mod_id)})
            if not mod:
                return None
            mod_name = mod.get("mod_name")
            result = self.collection.delete_one({"_id": ObjectId(mod_id)})
            if result.deleted_count > 0:
                return mod_name
            return None
        except Exception as e:
            logger.error(f"删除 mod 失败: {e}")
            return None

    def find_by_id(self, mod_id: str) -> Mod | None:
        try:
            mod = self.collection.find_one({"_id": ObjectId(mod_id)})
            if not mod:
                logger.error("Mod not found")
                return None
            mod = dict(mod)
            mod.pop("_id", None)
            return Mod.model_validate(mod)
        except Exception as e:
            logger.error(f"获取 mod 失败: {e}")
            return None



usersRepository = UsersCollection()
conversationsRepository = ConversationsCollection()
messagesRepository = MessagesCollection()
metaInfosRepository = MetaInfoCollection()



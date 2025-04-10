from pymongo import MongoClient
from config import settings
from model import UserInfo, ConversationInfo, MessageInfo
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
    
    def insert_one(self, user: UserInfo) -> bool:
        try:
            # replace id into _id
            tmp = user.model_dump()
            tmp.pop("id")
            self.collection.insert_one(tmp)
            return True
        except Exception as e:
            logger.error(f"Error inserting user: {e}")
            return False

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

usersCollection = UsersCollection()
conversationsCollection = ConversationsCollection()
messagesCollection = MessagesCollection()



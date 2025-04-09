from pymongo import MongoClient
from config import settings
from model import UserInfo, ConversationInfo, MessageInfo
from bson import ObjectId
import logging


client = MongoClient(settings.MONGO_URL, serverSelectionTimeoutMS=3000)
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
            self.collection.insert_one(user.model_dump())
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
    
    def insert_one(self, conversation: ConversationInfo) -> bool:
        try:
            self.collection.insert_one(conversation.model_dump())
            return True
        except Exception as e:
            logger.error(f"Error inserting conversation: {e}")
            return False

class MessagesCollection:
    def __init__(self):
        self.collection = db["messages"]
    
    def find_all_by_conversation_id(self, conversation_id: ObjectId) -> list[MessageInfo]:
        messages = self.collection.find({"conversation_id": conversation_id})
        return [MessageInfo(**message) for message in messages]

    def insert_one(self, message: MessageInfo) -> bool:
        try:
            self.collection.insert_one(message.model_dump())
            return True
        except Exception as e:
            logger.error(f"Error inserting message: {e}")
            return False

usersCollection = UsersCollection()
conversationsCollection = ConversationsCollection()
messagesCollection = MessagesCollection()



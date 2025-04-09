from pymongo import MongoClient
from config import settings

client = MongoClient(settings.MONGODB_URL)
db = client["modhelper"]

users_collection = db["users"]
conversations_collection = db["conversations"]
messages_collection = db["messages"]

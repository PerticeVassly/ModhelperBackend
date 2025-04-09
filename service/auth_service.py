from fastapi import HTTPException
from db import users
from model import UserRegister, UserLogin
import bcrypt
from datetime import datetime

def handle_register(user: UserRegister):
    if users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    users.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password),
        "created_at": datetime.now()
    })
    return {"message": "User registered"}

def handle_login(user: UserLogin):
    db_user = users.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": str(db_user["_id"])}

def hash_password(password: str) -> str:
  return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
  return bcrypt.checkpw(password.encode(), hashed.encode())
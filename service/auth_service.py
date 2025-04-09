from fastapi import HTTPException, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from db import usersCollection
from model import UserRegister, UserLogin, UserInfo
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from config import settings
import logging
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

logger = logging.getLogger("service")

def handle_register(user: UserRegister):
    if usersCollection.find_one_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = hash_password(user.password)
    usersCollection.insert_one({
        "username": user.username,
        "password": hashed_password,
        "email": user.email
    })
    logger.info(f"User {user.username} registered successfully")
    return {"User registered"}

def handle_login(user: UserLogin):
    db_user = usersCollection.find_one_by_username(user.username)
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": str(db_user.id)})
    logger.info(f"User {user.username} logged in successfully")
    return {"access_token": token, "token_type": "bearer"}

def hash_password(password: str) -> str:
  return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
  return bcrypt.checkpw(password.encode(), hashed.encode())

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInfo:
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = ObjectId(payload["sub"]) 
    return usersCollection.find_one(user_id=user_id) or HTTPException(status_code=404, detail="User not found")

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


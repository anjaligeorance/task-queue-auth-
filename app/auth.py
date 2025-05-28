from jose import jwt
from datetime import datetime, timedelta
from pymongo import MongoClient
import hashlib

SECRET_KEY = "your_secret_key"  # must match main.py
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

client = MongoClient("mongodb://localhost:27017/")
db = client["your_db"]
users_collection = db["users"]


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_user(username: str, password: str):
    user = users_collection.find_one({"username": username})
    if user and user["hashed_password"] == hash_password(password):
        return user
    return None


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.tasks import publish_task
from app.cache import redis_client
from app.auth import (
    create_access_token,
    authenticate_user,
    hash_password,
    users_collection,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

print("Starting FastAPI app...")

app = FastAPI()

# === JWT Auth Setup ===
SECRET_KEY = "your_secret_key"  # Must match app.auth
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# === Get Current User from JWT ===
def get_current_user(token: str = Depends(oauth2_scheme)):
    print("Received token:", token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Decoded payload:", payload)
        username: str = payload.get("sub")
        if username is None:
            print("No 'sub' in token")
            raise credentials_exception
        return username
    except JWTError as e:
        print("JWT decode error:", str(e))
        raise credentials_exception


# === Register User ===
@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    existing_user = users_collection.find_one({"username": username})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = hash_password(password)
    users_collection.insert_one({"username": username, "hashed_password": hashed_password})
    return {"msg": "User registered successfully"}


# === Login and Generate JWT Token ===
@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(
        data={"sub": form.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


# === Root API (GET /) ===
@app.get("/")
def read_root(current_user: str = Depends(get_current_user)):
    return {"message": "Task Queue API with RabbitMQ, Redis, Mongo", "user": current_user}


# === Submit Task (POST /submit-task) ===
@app.post("/submit-task")
async def submit_task(request: Request, current_user: str = Depends(get_current_user)):
    data = await request.json()
    task_id = publish_task(data)
    return {"message": "Task submitted", "task_id": task_id, "user": current_user}


# === Get Task Status (GET /task-status/{task_id}) ===
@app.get("/task-status/{task_id}")
def get_status(task_id: str, current_user: str = Depends(get_current_user)):
    status = redis_client.get(task_id)
    status_str = "not found" if status is None else status.decode() if isinstance(status, bytes) else status
    return {"task_id": task_id, "status": status_str, "user": current_user}


print("Finished setting up FastAPI app.")

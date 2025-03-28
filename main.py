import shutil
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os
import uuid
import random

app = FastAPI()
QUOTES_FILE = "message.json"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_quotes():
    if not os.path.exists(QUOTES_FILE):
        return []
    with open(QUOTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_quotes(quotes):
    with open(QUOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(quotes, f, ensure_ascii=False, indent=4)

class Quote(BaseModel):
    text_message: str
    username: str
    img_name: str = None


@app.get("/chat")
def get_quotes():
    return load_quotes()

@app.post("/send_message")
def add_quote(quote: Quote):
    quotes = load_quotes()

    message = quote.dict()
    message["id"] = str(uuid.uuid4())

    quotes.append(message)

    save_quotes(quotes)
    return {"message": "Сообщение отправлено"}




@app.get("/")
def hello():
    return {"message": "Chat Api"}




UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/images", StaticFiles(directory=UPLOAD_DIR), name="images")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    filename = str(random.randint(100000,999999)) + "." + file.filename.split(".")[-1]
    file_path = os.path.join(UPLOAD_DIR, filename  )
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении файла: {str(e)}")
    return {"filename": filename, "message": "Файл успешно загружен"}



class Add_avatar(BaseModel):
    username: str
    img_name: str = None


AVATARFILES = "Avatars.json"

def load_avatars():
    if not os.path.exists(AVATARFILES):
        return {}
    with open(AVATARFILES, "r", encoding="utf-8") as f:
        return json.load(f)

def save_avatars(quotes):
    with open(AVATARFILES, "w", encoding="utf-8") as f:
        json.dump(quotes, f, ensure_ascii=False, indent=4)


@app.post("/add_avatar")
async def add_avatar(newavatar: Add_avatar):
    av = load_avatars()

    av[newavatar.username] = newavatar.img_name

    save_avatars(av)

    return {"message": "ok"}

@app.get("/get_avatar/{user_name}")
async def get_avatar(user_name: str):
    av = load_avatars() 

    filename = av.get(user_name)

    if filename == None:
        return {"filename":"image.png"}

    return {"filename": filename}


@app.get("/get_users_list")
async def get_users_list():
    av : dict = load_avatars() 
    return list(av.keys())

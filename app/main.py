from fastapi import FastAPI, UploadFile, File, Form
import os
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3
import pathlib
from datetime import datetime
from fastapi.responses import FileResponse

import cloudinary
import cloudinary.uploader

app = FastAPI()

# ---------------------------
# Cloudinary 設定
# ---------------------------
cloudinary.config(
    cloud_name="dwwzsuavh",
    api_key="339471142411895",
    api_secret="T8MaKXK1oyR0siB5YCz5pHZqz6w"
)

# ---------------------------
# 建立資料夾
# ---------------------------
os.makedirs("uploads/photos", exist_ok=True)

# ---------------------------
# 建立資料庫
# ---------------------------
conn = sqlite3.connect("checkins.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lat REAL,
    lng REAL,
    time TEXT,
    photo TEXT
)
""")

conn.commit()


# ---------------------------
# Model
# ---------------------------
class Checkin(BaseModel):
    lat: float
    lng: float


# ---------------------------
# 首頁
# ---------------------------
@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------
# GPS 打卡
# ---------------------------
@app.post("/checkin")
def add_checkin(data: Checkin):

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO checkins (lat,lng,time) VALUES (?,?,?)",
        (data.lat, data.lng, now)
    )

    conn.commit()

    return {
        "status": "success",
        "lat": data.lat,
        "lng": data.lng
    }


# ---------------------------
# 拍照打卡
# ---------------------------
@app.post("/checkin_photo")
async def checkin_photo(
    lat: float = Form(...),
    lng: float = Form(...),
    file: UploadFile = File(...)
):

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 上傳到 Cloudinary
    contents = await file.read()

    result = cloudinary.uploader.upload(contents)

    photo_url = result["secure_url"]

    cursor.execute(
        "INSERT INTO checkins(lat,lng,time,photo) VALUES(?,?,?,?)",
        (lat, lng, now, photo_url)
    )

    conn.commit()

    return {
        "status": "success",
        "photo": photo_url
    }


# ---------------------------
# 取得所有打卡
# ---------------------------
@app.get("/checkins")
def get_checkins():

    cursor.execute("SELECT lat,lng,time,photo FROM checkins")
    rows = cursor.fetchall()

    results = [
        {"lat": r[0], "lng": r[1], "time": r[2], "photo": r[3]}
        for r in rows
    ]

    return results


# ---------------------------
# static
# ---------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
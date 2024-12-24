import datetime
from typing import List
from fastapi import FastAPI, Depends, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from disaster_report import handle_disaster_report
import models
from database import SessionLocal, engine
from contextlib import asynccontextmanager
import os
import base64
from fastapi import Form

# lifespanイベントで起動時にDB作成
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("アプリ起動時: データベースを作成します...")
    print("データベース作成完了")
    yield  # アプリの動作を開始
    print("アプリ終了時: クリーンアップ処理")

# リクエストモデル
class LoginRequest(BaseModel):
    code: str
    password: str

# 位置情報用のモデル
class Location(BaseModel):
    latitude: float
    longitude: float

# メインのリクエスト用モデル
class DisasterRequest(BaseModel):
    disaster: str
    description: str
    isImportant: bool
    importance: int
    location: Location  # Locationモデルを使う
    images: list[str] = []  # ここで images を受け取れるようにする

# FastAPIアプリ本体
app = FastAPI(lifespan=lifespan)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のドメインのみ許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベースセッションの依存性
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "データベースが自動作成されました！"}

@app.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.administrative == request.code,
        models.User.password == request.password
    ).first()
    if user:
        return {"success": True}
    else:
        return {"success": False}

# 画像保存用ディレクトリ
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/disaster_report")
async def disaster_report(
    disaster: str = Form(...),
    description: str = Form(...),
    isImportant: bool = Form(...),
    importance: int = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    return await handle_disaster_report(
        disaster=disaster,
        description=description,
        isImportant=isImportant,
        importance=importance,
        latitude=latitude,
        longitude=longitude,
        images=images,
        db=db
    )

# 位置情報を返すエンドポイント
@app.get("/disaster_report")
async def get_disaster_reports(db: Session = Depends(get_db)):
    try:
        # Reportテーブルから全ての災害報告を取得
        reports = db.query(models.Report).all()
        
        # 位置情報（latitude, longitude）をリストとして返す
        location_data = []
        for report in reports:
            latitude, longitude = report.location.split(',')
            location_data.append({
                "report_id": report.support_id,
                "latitude": float(latitude),
                "longitude": float(longitude),
            })
        
        return {"success": True, "locations": location_data}
    
    except Exception as e:
        print(f"エラー詳細: {e}")
        raise HTTPException(status_code=500, detail=f"エラーが発生しました。エラー詳細: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8000))  # デフォルトポートを8000に変更
    uvicorn.run(app, host="0.0.0.0", port=port)

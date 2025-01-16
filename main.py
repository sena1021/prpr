import datetime
from typing import List
from fastapi import FastAPI, Depends, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import base64
from pydantic import BaseModel
from database import SessionLocal
import models
import logging

# ログの設定
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    images: List[str] = []  # ここで images を受け取れるようにする

# FastAPIアプリ本体
app = FastAPI()

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

# 画像保存用ディレクトリ
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

@app.post("/disaster_report")
async def disaster_report(request: DisasterRequest, db: Session = Depends(get_db)):
    try:
        # 画像の保存（Base64デコード）
        image_paths = []
        for i, base64_image in enumerate(request.images):
            try:
                # Base64画像データをデコードして保存
                image_data = base64.b64decode(base64_image)  # Base64をデコード
                file_name = f"image_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{i}.png"  # ファイル名生成
                file_path = os.path.join(UPLOAD_DIR, file_name)

                # ディスクに画像を保存
                with open(file_path, "wb") as f:
                    f.write(image_data)
                image_paths.append(file_path)

                logger.info(f"画像 {file_name} を保存しました")
            except Exception as e:
                logger.error(f"画像の保存中にエラーが発生しました: {e}")
                raise HTTPException(status_code=400, detail=f"画像の保存中にエラーが発生しました: {e}")

        # データベースに災害報告を保存
        new_report = models.Report(
            content=request.description,
            importance=request.importance,
            image=",".join(image_paths),  # 画像のファイルパスをカンマ区切りで保存
            location=f"{request.location.latitude},{request.location.longitude}",  # 位置情報を文字列として保存
            datetime=datetime.datetime.utcnow()  # 現在の日時を保存
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        logger.info("災害報告がデータベースに保存されました。")
        return {"success": True, "message": "災害報告が保存されました。", "report_id": new_report.support_id}
    
    except Exception as e:
        logger.error(f"サーバーエラーが発生しました: {str(e)}")
        raise HTTPException(status_code=500, detail=f"サーバーエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

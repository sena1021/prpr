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

@app.post("/disaster_report")
async def disaster_report(
    disaster: str = Form(...),
    description: str = Form(...),
    isImportant: bool = Form(...),
    importance: int = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    images: List[str] = Form(...),  # Base64形式の画像をリストで受け取る
    db: Session = Depends(get_db),
):
    try:
        # Base64画像データを保存し、ファイルパスを取得
        image_paths = []
        for i, base64_image in enumerate(images):
            try:
                # デコードして画像データに変換
                image_data = base64.b64decode(base64_image)
                file_name = f"image_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{i}.png"
                file_path = os.path.join(UPLOAD_DIR, file_name)
                
                # ディスクに保存
                with open(file_path, "wb") as f:
                    f.write(image_data)
                image_paths.append(file_path)
                
                logger.info(f"画像 {file_name} を保存しました")
            except Exception as e:
                logger.error(f"画像の保存中にエラーが発生しました: {e}")
                raise HTTPException(status_code=400, detail=f"画像の保存中にエラーが発生しました: {e}")

        # レポートをデータベースに保存
        new_report = models.Report(
            content=description,
            importance=importance,
            image=image_paths,  # 画像のファイルパスを保存
            location=f"{latitude},{longitude}",  # 位置情報を文字列として保存
            datetime=datetime.datetime.utcnow()
        )
        db.add(new_report)
        db.commit()

        logger.info("災害報告がデータベースに保存されました。")
        return {"success": True, "message": "災害報告が保存されました。"}
    
    except Exception as e:
        logger.error(f"サーバーエラーが発生しました: {str(e)}")
        raise HTTPException(status_code=500, detail=f"サーバーエラーが発生しました: {str(e)}")

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
        
        logger.info("災害報告の位置情報を返却しました。")
        return {"success": True, "locations": location_data}
    
    except Exception as e:
        logger.error(f"エラーが発生しました。エラー詳細: {str(e)}")
        raise HTTPException(status_code=500, detail=f"エラーが発生しました。エラー詳細: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

import datetime
from typing import List
from fastapi import FastAPI, Depends, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import File
from pydantic import BaseModel
from sqlalchemy.orm import Session
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

# 災害報告エンドポイント
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
    try:
        # アップロードされた画像をBase64エンコードして保存
        base64_images = []
        for image in images:
            image_bytes = await image.read()
            encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            base64_images.append(encoded_image)

        # データベースに新しいレポートを作成して保存
        report = models.Report(
            content=description,
            importance=importance,
            image=",".join(base64_images),
            location=f"{latitude},{longitude}",
            datetime=datetime.datetime.now(),
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        return {"success": True, "report_id": report.support_id}
    except Exception as e:
        db.rollback()
        print(f"エラー詳細: {e}")  # サーバーログに詳細を記録
        raise HTTPException(status_code=500, detail=f"データ保存中にエラーが発生しました。エラー詳細: {str(e)}")
    
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8000))  # デフォルトポートを8000に変更
    uvicorn.run(app, host="0.0.0.0", port=port)

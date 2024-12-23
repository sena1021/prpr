from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine
from contextlib import asynccontextmanager
import os  # osモジュールを追加

# lifespanイベントで起動時にDB作成
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("アプリ起動時: データベースを作成します...")
    models.Base.metadata.create_all(bind=engine)  # テーブル作成
    print("データベース作成完了")
    yield  # アプリの動作を開始
    print("アプリ終了時: クリーンアップ処理")

# リクエストモデル
class LoginRequest(BaseModel):
    code: str
    password: str

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

# government_tableからデータを取得するエンドポイント
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    try:
        # government_tableから全てのデータを取得
        users = db.query(models.User).all()
        # データを整形して返す
        return {
            "text": [
                {"id": user.id, "administrative": user.administrative, "password": user.password}
                for user in users
            ]
        }
    except Exception as e:
        # エラー発生時に例外を返す
        raise HTTPException(status_code=500, detail=f"データの取得中にエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 8000))  # デフォルトポートを8000に変更
    uvicorn.run(app, host="0.0.0.0", port=port)

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import SessionLocal, engine
from contextlib import asynccontextmanager

# lifespanイベントで起動時にDB作成
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("アプリ起動時: データベースを作成します...")
    models.Base.metadata.create_all(bind=engine)  # テーブル作成
    print("データベース作成完了")
    yield  # アプリの動作を開始
    print("アプリ終了時: クリーンアップ処理")

# FastAPIアプリ本体
app = FastAPI(lifespan=lifespan)

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

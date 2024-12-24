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


def handle_disaster_report(
    disaster: str,
    description: str,
    isImportant: bool,
    importance: int,
    latitude: float,
    longitude: float,
    images: List[UploadFile],
    db: Session
):
    try:
        # アップロードされた画像をBase64エンコードして保存
        base64_images = []
        for image in images:
            image_bytes = image.file.read()
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
    
from typing import List
from zoneinfo import ZoneInfo
from fastapi import FastAPI, Depends, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import base64
from pydantic import BaseModel, Field
from database import SessionLocal
import models
import logging
from datetime import datetime

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

class CommentRequest(BaseModel):
    comment: str

# 日本時間の現在日時を取得
jp_time = datetime.now(ZoneInfo("Asia/Tokyo"))

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

#ログインAPI
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
        # 現在の日時を取得（日本時間）
        jp_time = datetime.now(ZoneInfo("Asia/Tokyo"))

        # 画像の保存（Base64デコード）
        image_paths = []
        for i, base64_image in enumerate(request.images):
            try:
                # Base64画像データをデコードして保存
                image_data = base64.b64decode(base64_image)
                file_name = f"image_{jp_time.strftime('%Y%m%d%H%M%S')}_{i}.png"  # ファイル名生成
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
            disaster=request.disaster,
            content=request.description,
            importance=request.importance,
            image=",".join(image_paths),  # 画像のファイルパスをカンマ区切りで保存
            location=f"{request.location.latitude},{request.location.longitude}",  # 位置情報を文字列として保存
            datetime=jp_time,  # 現在の日時を保存
            status=0  # 状態を0で保存
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        logger.info("災害報告がデータベースに保存されました。")
        return {"success": True, "message": "災害報告が保存されました。", "report_id": new_report.support_id}
    
    except Exception as e:
        logger.error(f"サーバーエラーが発生しました: {str(e)}")
        raise HTTPException(status_code=500, detail=f"サーバーエラーが発生しました: {str(e)}")

@app.get("/disaster")
async def get_disaster_reports(db: Session = Depends(get_db)):
    try:
        # Reportテーブルからすべての災害報告を取得
        reports = db.query(models.Report).all()
        
        # 各報告の情報を返す形式に変換
        report_data = []
        for report in reports:
            # status が 5 のレポートをスキップ
            if report.status == 5:
                continue
            
            # 位置情報（latitude, longitude）の分解
            latitude, longitude = report.location.split(',')
            
            # 画像をBase64形式に変換
            base64_images = []
            for image_path in report.image.split(','):
                try:
                    with open(image_path, "rb") as image_file:
                        # 画像を読み込みBase64にエンコード
                        image_data = image_file.read()
                        base64_image = base64.b64encode(image_data).decode('utf-8')
                        base64_images.append(base64_image)
                except FileNotFoundError:
                    # 画像が見つからない場合のエラーハンドリング
                    base64_images.append(None)  
            
            report_data.append({
                "report_id": report.support_id,
                "disaster": report.disaster,
                "description": report.content,
                "isImportant": report.importance > 5,  # importanceが5以上で重要と判断
                "importance": report.importance,
                "location": {
                    "latitude": float(latitude),
                    "longitude": float(longitude)
                },
                "images": base64_images,  # Base64エンコードされた画像
                "datetime": report.datetime,
                "status": report.status
            })
        
        logger.info("災害報告の情報を返却しました。")
        return {"success": True, "reports": report_data}
    
    except Exception as e:
        logger.error(f"エラーが発生しました。エラー詳細: {str(e)}")
        raise HTTPException(status_code=500, detail=f"エラーが発生しました。エラー詳細: {str(e)}")

# 災害報告の削除（ステータス変更）API
@app.delete("/disaster/{report_id}")
async def update_disaster_status(report_id: int, db: Session = Depends(get_db)):
    try:
        # 対象のレポートを取得
        report = db.query(models.Report).filter(models.Report.support_id == report_id).first()
        
        if not report:
            logger.warning(f"指定されたレポートID {report_id} が見つかりませんでした。")
            raise HTTPException(status_code=404, detail="指定されたレポートが見つかりません。")
        
        # ステータスを 5 に変更
        report.status = 5
        db.commit()
        logger.info(f"レポートID {report_id} のステータスを 5 に変更しました。")
        
        return {"success": True, "message": f"レポートID {report_id} のステータスを 5 に変更しました。"}
    
    except Exception as e:
        logger.error(f"ステータス変更中にエラーが発生しました: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ステータス変更中にエラーが発生しました: {str(e)}")

# 災害報告のステータス変更API
@app.post("/disaster/{report_id}/swap_status")
async def swap_disaster_status(report_id: int, db: Session = Depends(get_db)):
    try:
        report = db.query(models.Report).filter(models.Report.support_id == report_id).first()

        if not report:
            raise HTTPException(status_code=404, detail="指定されたレポートが見つかりません。")

        # ステータスを 0 → 1 → 2 → 0 のように変更
        report.status = (report.status + 1) % 3
        db.commit()
        db.refresh(report)

        return {"success": True, "message": "ステータスを変更しました。", "new_status": report.status}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ステータス変更中にエラーが発生しました: {str(e)}")


@app.post("/disaster/{report_id}/comment")
async def disaster_comment(report_id: int, request: CommentRequest, db: Session = Depends(get_db)):
    try:
        report = db.query(models.Report).filter(models.Report.support_id == report_id).first()

        if not report:
            logger.warning(f"レポートID {report_id} が見つかりません。")
            raise HTTPException(status_code=404, detail="指定されたレポートが見つかりません。")

        # 受け取ったコメントを設定
        report.comment = request.comment
        db.flush()  # 変更を確定前に適用
        db.commit()
        db.refresh(report)

        logger.info(f"レポートID {report_id} にコメントを追加しました。")
        return {"success": True, "message": "コメントを追加しました。", "new_comment": report.comment}
 
    except Exception as e:
        logger.error(f"コメント追加中にエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"コメント追加中にエラー: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

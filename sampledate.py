from database import SessionLocal
import models
from sqlalchemy.orm import Session
from datetime import datetime

# サンプルユーザー作成
def create_sample_user(db: Session):
    user = models.User(
        administrative=1,  # サンプルの管理者コード
        password="1111"  # サンプルパスワード
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# サンプル報告作成
def create_sample_report(db: Session):
    report = models.Report(
        content="地震が発生しました。建物が倒壊しています。",
        importance=5,
        image="sample_image_base64_data_here",  # サンプルのBase64データ
        location="35.6895,139.6917",  # 緯度経度（例：東京の位置）
        datetime=datetime.utcnow()
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

# サンプルデータの挿入
def create_sample_data():
    db = SessionLocal()
    try:
        # ユーザーと報告を作成
        create_sample_user(db)
        create_sample_report(db)
        print("サンプルデータを作成しました。")
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()

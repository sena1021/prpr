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
        disaster="地震",  # 災害の種類
        content="地震が発生しました。建物が倒壊しています。",
        importance=5,
        image="sample_base64_image_data",  # サンプルのBase64画像データ
        location="35.6895,139.6917",  # 緯度経度（例：東京の位置）
        status=0,  # 初期状態
        datetime=datetime.utcnow()  # 現在時刻
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

# サンプルデータの挿入
def create_sample_data():
    db = SessionLocal()
    try:
        # ユーザーと報告データを作成
        user = create_sample_user(db)
        report = create_sample_report(db)
        print("サンプルデータを作成しました。")
        print(f"ユーザー: {user}")
        print(f"報告: {report}")
    finally:
        db.close()

# スクリプトのエントリーポイント
if __name__ == "__main__":
    create_sample_data()

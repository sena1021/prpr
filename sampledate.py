from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from datetime import datetime  # 修正箇所

# データベースセッションの準備
db: Session = SessionLocal()

# ユーザーテーブルにサンプルデータを挿入
def insert_sample_user():
    try:
        user1 = models.User(administrative=1, password="1111")
        user2 = models.User(administrative=2, password="2222")
        
        db.add(user1)
        db.add(user2)
        db.commit()
        print("ユーザーデータを挿入しました。")
    except Exception as e:
        db.rollback()
        print(f"ユーザーデータ挿入中にエラーが発生しました: {e}")

# レポートテーブルにサンプルデータを挿入
def insert_sample_report():
    try:
        report1 = models.Report(
            content="洪水が発生しています。",
            importance=5,
            image="sample_base64_image_data_1,sample_base64_image_data_2",
            location="35.6895,139.6917",
            datetime=datetime.now()  # 修正箇所
        )
        report2 = models.Report(
            content="地震による建物の倒壊あり。",
            importance=4,
            image="sample_base64_image_data_3",
            location="34.0522,118.2437",
            datetime=datetime.now()  # 修正箇所
        )

        db.add(report1)
        db.add(report2)
        db.commit()
        print("レポートデータを挿入しました。")
    except Exception as e:
        db.rollback()
        print(f"レポートデータ挿入中にエラーが発生しました: {e}")

# データベースの内容を確認
def fetch_all_data():
    try:
        users = db.query(models.User).all()
        reports = db.query(models.Report).all()

        print("=== ユーザーデータ ===")
        for user in users:
            print(f"ID: {user.id}, Administrative: {user.administrative}, Password: {user.password}")

        print("\n=== レポートデータ ===")
        for report in reports:
            print(f"Support ID: {report.support_id}, Content: {report.content}, Importance: {report.importance}, "
                  f"Location: {report.location}, Datetime: {report.datetime}, Images: {report.image}")
    except Exception as e:
        print(f"データ取得中にエラーが発生しました: {e}")

# サンプルデータを挿入して確認
if __name__ == "__main__":
    insert_sample_user()
    insert_sample_report()
    fetch_all_data()

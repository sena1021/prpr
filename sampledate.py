from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models

# データベースの初期化
models.Base.metadata.create_all(bind=engine)

# サンプルデータを挿入
def create_sample_data():
    db: Session = SessionLocal()
    try:
        # Userテーブルにサンプルデータを挿入
        user1 = models.User(administrative=1, password="1111")
        user2 = models.User(administrative=2, password="2222")

        # Reportテーブルにサンプルデータを挿入
        report1 = models.Report(
            content="道路が壊れています",
            importance=2,
            image="image1.png",
            location="東京都新宿区",
            datetime="2024-12-23 12:00:00"
        )
        report2 = models.Report(
            content="信号が故障しています",
            importance=1,
            image="image2.png",
            location="大阪市北区",
            datetime="2024-12-24 09:30:00"
        )

        # データをセッションに追加
        db.add(user1)
        db.add(user2)
        db.add(report1)
        db.add(report2)

        # コミットしてデータを保存
        db.commit()

        print("サンプルデータを挿入しました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        db.rollback()
    finally:
        db.close()

# 実行
if __name__ == "__main__":
    create_sample_data()

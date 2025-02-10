from sqlalchemy.orm import Session
from database import SessionLocal
import models
import datetime

# データベースセッションを作成
db: Session = SessionLocal()

# ユーザーのテストデータ
test_user = models.User(administrative=1, password="1")
db.add(test_user)

# 災害報告のテストデータ（5件）
test_reports = [
    models.Report(
        disaster="地震",
        content="強い揺れを観測しました。",
        comment="余震に注意してください。",
        importance=8,
        image="test_image1.png",
        location="35.6895,139.6917",  # 東京
        status=0,
        datetime=datetime.datetime.utcnow()
    ),
    models.Report(
        disaster="台風",
        content="暴風雨により停電が発生。",
        comment="安全な場所へ避難してください。",
        importance=7,
        image="test_image2.png",
        location="33.5904,130.4017",  # 福岡
        status=1,
        datetime=datetime.datetime.utcnow()
    ),
    models.Report(
        disaster="洪水",
        content="川の水位が上昇し、避難が必要。",
        comment="近隣住民に避難勧告。",
        importance=9,
        image="test_image3.png",
        location="34.6937,135.5023",  # 大阪
        status=2,
        datetime=datetime.datetime.utcnow()
    ),
    models.Report(
        disaster="火災",
        content="大規模な火災が発生。",
        comment="消防隊が出動。",
        importance=10,
        image="test_image4.png",
        location="35.0116,135.7681",  # 京都
        status=0,
        datetime=datetime.datetime.utcnow()
    ),
    models.Report(
        disaster="津波",
        content="沿岸部に津波警報が発令。",
        comment="高台へ避難してください。",
        importance=10,
        image="test_image5.png",
        location="38.2682,140.8694",  # 仙台
        status=1,
        datetime=datetime.datetime.utcnow()
    ),
]

# データベースに追加
db.add_all(test_reports)

# コミットして保存
db.commit()

# セッションを閉じる
db.close()

print("テストデータ5件を作成しました。")

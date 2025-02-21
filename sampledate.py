from sqlalchemy.orm import sessionmaker
from database import engine
from models import User, Report
import datetime as dt

# セッションの作成
Session = sessionmaker(bind=engine)
session = Session()

# ユーザーデータの挿入
users = [
    User(administrative=1, password="1")
]
session.add_all(users)
session.commit()

# レポートデータの挿入
reports = [
    Report(disaster="地震", content="札幌市北区で震度5の地震が発生", comment="被害状況を調査中", 
           importance=3, image="", location="43.0902,141.3468", status=1, datetime=dt.datetime.utcnow()),
    Report(disaster="火災", content="札幌市中央区のビルで火災が発生", comment="消防隊が出動済み", 
           importance=4, image="", location="43.0554,141.3405", status=2, datetime=dt.datetime.utcnow()),
    Report(disaster="大雪", content="札幌市南区で大雪により交通が麻痺", comment="除雪作業を実施中", 
           importance=2, image="", location="42.9908,141.3533", status=1, datetime=dt.datetime.utcnow()),
]
session.add_all(reports)
session.commit()

print("サンプルデータを挿入しました。")

from database import Base,engine
import models
from sqlalchemy import Column, Integer, String, Text, DateTime
import datetime as dt

# ユーザーテーブル定義
class User(Base):
    __tablename__ = "government_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    administrative = Column(Integer, unique=True, nullable=False)  # 必須項目
    password = Column(String, unique=True, nullable=False)         # 必須項目

class Report(Base):
    __tablename__ = "report_data_table"

    support_id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)  # 説明は必須項目
    importance = Column(Integer, nullable=False)  # 必須項目
    image = Column(Text, nullable=True)  # Base64画像を格納、必須ではない
    location = Column(String, nullable=False)  # 緯度経度は必須項目
    datetime = Column(DateTime, default=dt.datetime.utcnow, nullable=False)  # 現在日時をデフォルト設定

# 既存のテーブルを削除してから再作成
# models.Base.metadata.drop_all(bind=engine)  # 全てのテーブルを削除
models.Base.metadata.create_all(bind=engine)  # 新しいテーブルを作成
print("データベースを再作成しました。")

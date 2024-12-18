from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLiteデータベースファイルのパス
DATABASE_URL = "sqlite:///./sqlite.db"

# データベースエンジンの作成
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()

from sqlalchemy import Column, Integer, String
from database import Base

# ユーザーテーブル定義
class User(Base):
    __tablename__ = "government_table"

    id = Column(Integer, primary_key = True, autoincrement = True)
    administrative = Column(Integer,unique = True)
    password = Column(String,unique = True)

class Report(Base):
    __tablename__ = "report_data_table"

    support_id	= Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String)
    importance = Column(Integer)
    image = Column(String)
    location = Column(String)
    datetime = Column(String)			
 			
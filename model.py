#!/usr/bin/env python
#coding:utf-8
"""
法律全文检索模型
"""
import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column,create_engine,String,Text

baseDir = os.path.dirname(__file__)
dbPath = os.path.join(baseDir,'law.db')

engine = create_engine('sqlite:///%s'%dbPath)
Base = declarative_base()
DBsession = sessionmaker(bind=engine)
session = DBsession()

class Law(Base):
    __tablename__ = 'law'

    id = Column(String(48),primary_key=True)
    title = Column(String(48))
    type = Column(String(48))
    publishDepartment = Column(String(48))
    publishDate = Column(String(48))
    effectDate = Column(String(48))
    loseEffectDate = Column(String(48))
    status = Column(String(48))
    content = Column(Text)

    #创建表
    @staticmethod
    def init_db():
        pass
        Base.metadata.create_all(engine)

    @staticmethod
    def drop_db():
        pass
        Base.metadata.drop_all(engine)
if __name__ == '__main__':
    pass
    Law.init_db()

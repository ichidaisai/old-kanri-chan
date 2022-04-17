# -*- coding: utf-8 -*-

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import BIGINT, CHAR
import discord.utils

# MySQL データベースの利用準備
DATABASE = 'mysql://%s:%s@%s/%s?charset=utf8mb4' % (
    "app", # ユーザー名
    "app", # パスワード
    "db", # MySQL サーバーのホスト名
    "app", # データベース名
)

ENGINE = create_engine(
    DATABASE,
    echo = True, # True にすると、実行のたびに SQL がログに出力される。
    pool_pre_ping = True,
    convert_unicode = False
)
session = scoped_session(
    sessionmaker(
        autocommit = False,
        autoflush = False,
        bind = ENGINE
    )
)

Base = declarative_base()
Base.query = session.query_property()

# テーブル モデル: `role` - ロールの情報を格納する
class Role(Base):
    __tablename__ = 'role'
    __table_args__=({"mysql_charset": "utf8mb4"})
    id = Column('id', BIGINT(unsigned = True), primary_key = True, unique = True, nullable = False)
    name = Column('name', VARCHAR(300))
    chat_tc = Column('chat_tc', BIGINT(unsigned = True))
    post_tc = Column('post_tc', BIGINT(unsigned = True))

Base.metadata.create_all(bind=ENGINE)

# addGroup: ロールをボットに認識させる（データベースに登録する）
def addGroup(id, guild):
    role = Role()
    role.id = id
    role.name = guild.get_role(int(id)).name

    session.add(role)
    session.commit()

# setChatTc: チャット用テキストチャンネルをボットに認識させる（データベースに登録する）
def setChatTc(id, tc):
    role = session.query(Role). \
           filter(Role.id == id). \
           first()
    
    role.chat_tc = tc
    session.commit()

# setPostTc: ファイル提出用テキストチャンネルをボットに認識させる（データベースに登録する）
def setPostTc(id, tc):
    role = session.query(Role). \
           filter(Role.id == id). \
           first()
    
    role.post_tc = tc
    session.commit()

# -*- coding: utf-8 -*-

# 外部ライブラリ
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import BIGINT, CHAR
import discord.utils

# MySQL データベースの利用準備
DATABASE = "mysql://%s:%s@%s/%s?charset=utf8mb4" % (
    "app",  # ユーザー名
    "app",  # パスワード
    "db",  # MySQL サーバーのホスト名
    "app",  # データベース名
)

ENGINE = create_engine(
    DATABASE,
    echo=True,  # True にすると、実行のたびに SQL がログに出力される。
    pool_pre_ping=True,
    convert_unicode=False,
)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=ENGINE))

Base = declarative_base()
Base.query = session.query_property()

# テーブル モデル: `role` - ロールの情報を格納する
class Role(Base):
    __tablename__ = "role"
    __table_args__ = {"mysql_charset": "utf8mb4"}
    id = Column(
        "id", BIGINT(unsigned=True), primary_key=True, unique=True, nullable=False
    )
    name = Column("name", VARCHAR(300))
    chat_tc = Column("chat_tc", BIGINT(unsigned=True))
    post_tc = Column("post_tc", BIGINT(unsigned=True))


# テーブル モデル: `item` - 提出物の情報を格納する
## id: 提出物の一意な ID。自動インクリメントなので、INSERT の際に手動で指定することはない。
## name: 提出物の名前。
## limit: 提出期限。YYYY-MM-DD-HH-mm
## target: その提出物を提出するべきロールの ID。ID は role テーブルの id と対応するようにする。
## verified: その提出物が委員会サイドから承認されたか。
## format: 提出物の形式。`file` または `plain` で、既定は `file`。
class Item(Base):
    __tablename__ = "item"
    __table_args__ = {"mysql_charset": "utf8mb4"}
    id = Column(
        "id",
        BIGINT(unsigned=True),
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True,
    )
    name = Column("name", VARCHAR(300))
    limit = Column("limit", DateTime)
    target = Column("target", BIGINT(unsigned=True))
    verified = Column("verified", Boolean)
    format = Column("format", VARCHAR(300), default="file")


Base.metadata.create_all(bind=ENGINE)

# addRole: ロールをボットに認識させる（データベースに登録する）
def addRole(id, guild):
    role = Role()
    role.id = id
    role.name = guild.get_role(int(id)).name

    session.add(role)
    session.commit()


# addRole: ロールをボットから削除する（データベースから削除する）
def delRole(id, guild):
    session.query(Role).filter(Role.id == id).delete()
    session.commit()


# setChatTc: チャット用テキストチャンネルをボットに認識させる（データベースに登録する）
def setChatTc(id, tc):
    exists = session.query(Role).filter(Role.id == id).first()
    if exists is None:
        return False
    else:
        role = session.query(Role).filter(Role.id == id).first()

        role.chat_tc = tc
        session.commit()
        return True


# setPostTc: ファイル提出用テキストチャンネルをボットに認識させる（データベースに登録する）
def setPostTc(id, tc):
    exists = session.query(Role).filter(Role.id == id).first()
    if exists is None:
        return False
    else:
        role = session.query(Role).filter(Role.id == id).first()

        role.post_tc = tc
        session.commit()
        return True


# addItem: ボットに提出物を登録する（データベースに登録する）
def addItem(name, limit, target, format):
    item = Item()
    item.name = name
    item.limit = limit
    item.target = target
    item.verified = False

    session.add(item)
    session.commit()

    return item.id


# delItem: ボットから提出物を削除する（データベースから削除する）
## id: 提出物の ID
def delItem(id):
    query = session.query(Item).filter(Item.id == id)
    result = session.query(query.exists()).scalar()

    if result is True:
        session.query(Item).filter(Item.id == id).delete()
        session.commit()
        return True
    else:
        return False


# showItem: ボットに登録されている提出物のうち、特定のロールが提出するべきものを返す。
## role_id: Discord のロール ID
def showItem(role_id):
    items = session.query(Item).filter(Item.target == role_id).all()
    return items


# getRole: チャンネルに紐付けられているロールの Discord 上での ID を返す。
def getRole(channel_id):
    role = (
        session.query(Role)
        .filter(or_(Role.chat_tc == int(channel_id), Role.post_tc == int(channel_id)))
        .first()
    )
    if role is None:
        return None
    else:
        return str(role.id)


# getItemName: 提出物の ID から、提出物の名前を返す
def getItemName(id):
    query = session.query(Item).filter(Item.id == id).first()
    result = session.query(query.exists()).scalar()

    if result is True:
        return str(item.name)
    else:
        return False


# getItemTarget: 提出物の ID から、提出物の対象者の Discord 上のロール ID を返す
def getItemTarget(id):
    item = session.query(Item).filter(Item.id == id).first()
    return str(item.target)


# getItemLimit: 提出物の ID から、提出物の期限を datetime 型で返す
def getItemLimit(id):
    item = session.query(Item).filter(Item.id == id).first()
    return item.limit

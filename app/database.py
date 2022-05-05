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
    parent_role = Column("parent_role", BIGINT(unsigned=True))
    chat_tc = Column("chat_tc", BIGINT(unsigned=True))
    post_tc = Column("post_tc", BIGINT(unsigned=True))


# テーブル モデル: `parent_role` - 親ロールの情報を格納する
## id: Discord のロール ID
## type: `staff` / `member`
class ParentRole(Base):
    __tablename__ = "parent_role"
    __table_args__ = {"mysql_charset": "utf8mb4"}
    id = Column(
        "id", BIGINT(unsigned=True), primary_key=True, unique=True, nullable=False
    )
    type = Column("type", VARCHAR(300))
    notify_tc = Column("notify_tc", BIGINT(unsigned=True), nullable=True, default=None)


# テーブル モデル: `Config` - チャンネル カテゴリの情報等、ボット全体に関わる情報を格納する
class Config(Base):
    __tablename__ = "config"
    __table_args__ = {"mysql_charset": "utf8mb4"}
    key = Column("key", VARCHAR(300), primary_key=True, unique=True, nullable=False)
    value = Column("value", VARCHAR(300))


# テーブル モデル: `item` - 提出先の情報を格納する
## id: 提出先の一意な ID。自動インクリメントなので、INSERT の際に手動で指定することはない。
## name: 提出先の名前。
## limit: 提出期限。YYYY-MM-DD-HH-mm
## target: その提出先を提出するべきロールの ID。ID は role テーブルの id と対応するようにする。
## handler: その提出先を作成したロールの ID。
## verified: その提出先が委員会サイドから承認されたか。
## format: 提出先の形式。`file` または `plain` で、既定は `file`。
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
    handler = Column("handler", BIGINT(unsigned=True))
    format = Column("format", VARCHAR(300), default="file")


class Submission(Base):
    __tablename__ = "submission"
    __table_args__ = {"mysql_charset": "utf8mb4"}
    id = Column(
        "id",
        BIGINT(unsigned=True),
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True,
    )
    item_id = Column("item_id", BIGINT(unsigned=True))
    datetime = Column("datetime", DateTime)

    # filename: format が file のとき参照。実体ファイルへのパスを格納する。
    # plain: format が plain のとき参照。プレーンテキストの中身を格納する。
    path = Column("path", VARCHAR(500), nullable=True)
    filename = Column("filename", VARCHAR(500), nullable=True)
    plain = Column("plain", VARCHAR(300), nullable=True)

    target = Column("target", BIGINT(unsigned=True))
    author = Column("author", BIGINT(unsigned=True))
    author_role = Column("author_role", BIGINT(unsigned=True))
    verified = Column("verified", Boolean, default=False)
    format = Column("format", VARCHAR(300), default="file")


Base.metadata.create_all(bind=ENGINE)

# setChatCategory: チャット用テキストチャンネルの親カテゴリーを設定する
def setChatCategory(id):
    exists = session.query(Config).filter(Config.key == "chat_category").first()

    if exists is None:
        # `chat_category` キーが存在しないとき、INSERT 文を発行する
        config = Config()
        config.key = "chat_category"
        config.value = id

        session.add(config)
        session.commit()
    else:
        # `chat_category` キーが存在するとき、UPDATE 文を発行する
        exists.value = id
        session.commit()


# setPostCategory: チャット用テキストチャンネルの親カテゴリーを設定する
def setPostCategory(id):
    exists = session.query(Config).filter(Config.key == "post_category").first()

    if exists is None:
        # `post_category` キーが存在しないとき、INSERT 文を発行する
        config = Config()
        config.key = "post_category"
        config.value = id

        session.add(config)
        session.commit()
    else:
        # `post_category` キーが存在するとき、UPDATE 文を発行する
        exists.value = id
        session.commit()

# setNotifyCategory: 新規提出物の通知用テキストチャンネルの親カテゴリーを設定する
def setNotifyCategory(id):
    exists = session.query(Config).filter(Config.key == "notify_category").first()

    if exists is None:
        # `post_category` キーが存在しないとき、INSERT 文を発行する
        config = Config()
        config.key = "notify_category"
        config.value = id

        session.add(config)
        session.commit()
    else:
        # `post_category` キーが存在するとき、UPDATE 文を発行する
        exists.value = id
        session.commit()


# addRole: ロールをボットに認識させる（データベースに登録する）
def addRole(id, guild):
    exists = session.query(Role).filter(Role.id == int(id)).first()

    if exists:
        return False
    else:
        role = Role()
        role.id = id
        role.name = guild.get_role(int(id)).name

        session.add(role)
        session.commit()
        return True


# addRole: ロールをボットから削除する（データベースから削除する）
def delRole(id, guild):
    exists = session.query(Role).filter(Role.id == int(id)).first()
    if exists:
        session.delete(exists)
        session.commit()
        return True
    else:
        return False


# setStaffRole: スタッフ用ロールを設定する
def setStaffRole(id):
    exists = session.query(Config).filter(Config.key == "staff_role").first()

    if exists:
        # `post_category` キーが存在するとき、UPDATE 文を発行する
        exists.value = id
        session.commit()
        return True
    else:
        # `post_category` キーが存在しないとき、INSERT 文を発行する
        config = Config()
        config.key = "staff_role"
        config.value = id

        session.add(config)
        session.commit()
        return True


# setGuild: ボットを使用する対象サーバーを設定する
def setGuild(guild_id):
    exists = session.query(Config).filter(Config.key == "guild").first()

    if exists:
        # `post_category` キーが存在するとき、UPDATE 文を発行する
        exists.value = guild_id
        session.commit()
        return True
    else:
        # `post_category` キーが存在しないとき、INSERT 文を発行する
        config = Config()
        config.key = "guild"
        config.value = guild_id

        session.add(config)
        session.commit()
        return True

# setBotTc: 管理用コマンドを実行するためのテキストチャンネルをボットに設定する
def setBotTc(id):
    key = "bot_tc"
    exists = session.query(Config).filter(Config.key == key).first()

    if exists:
        # `bot_tc` キーが存在するとき、UPDATE 文を発行する
        exists.value = id
        session.commit()
        return True
    else:
        # `bot_tc` キーが存在しないとき、INSERT 文を発行する
        config = Config()
        config.key = key
        config.value = id

        session.add(config)
        session.commit()
        return True

# getBotTc: 管理用コマンドを実行するためのテキストチャンネルの ID を返す
def getBotTc():
    exists = session.query(Config).filter(Config.key == "bot_tc").first()
    if exists:
        return int(exists.value)
    else:
        return None


# getGuild: ボットを使用するサーバーの ID を返す
def getGuild():
    exists = session.query(Config).filter(Config.key == "guild").first()
    if exists:
        return exists.value
    else:
        return None


# getStaffRole: スタッフ用の Discord ロールの ID を返す。未設定のときは None を返す。
def getStaffRole():
    exists = session.query(Config).filter(Config.key == "staff_role").first()

    if exists:
        return exists.value
    else:
        return None


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
    if exists:
        role = session.query(Role).filter(Role.id == id).first()

        role.post_tc = tc
        session.commit()
        return True
    else:
        return False


# addItem: ボットに提出先を登録する（データベースに登録する）
def addItem(name, limit, target, handler, format):
    item = Item()
    item.name = name
    item.limit = limit
    item.target = target
    item.handler = handler
    item.format = format

    session.add(item)
    session.commit()

    return item.id


# delItem: ボットから提出先を削除する（データベースから削除する）
## id: 提出先の ID
def delItem(id):
    query = session.query(Item).filter(Item.id == id)
    result = session.query(query.exists()).scalar()

    if result:
        session.query(Item).filter(Item.id == id).delete()
        session.commit()
        return True
    else:
        return False


# showItem: ボットに登録されている提出先のうち、特定のロールが提出するべきものを返す。
## role_id: Discord のロール ID
## format:
## all: すべての提出形式の提出先を返す
## file: ファイル形式の提出先を返す
## plain: プレーンテキスト形式の提出先を返す
def showItem(role_id, format):
    if format == "all":
        items = session.query(Item).filter(Item.target == role_id).all()
        return items
    elif format == "file":
        items = (
            session.query(Item)
            .filter(Item.target == role_id, Item.format == "file")
            .all()
        )
        return items
    elif format == "plain":
        items = (
            session.query(Item)
            .filter(Item.target == role_id, Item.format == "plain")
            .all()
        )
        return items
    else:
        return None


# addSubmit: ボットに提出されたファイルまたはプレーンテキストを登録する（データベースに登録する）
def addSubmit(
    item_id, datetime, filename, path, plain, author, author_role, target, format
):
    submission = Submission()

    submission.item_id = item_id
    submission.datetime = datetime
    submission.format = format
    submission.target = target
    submission.author = author
    submission.author_role = author_role

    if format == "file":
        submission.filename = filename
        submission.path = path
    elif format == "plain":
        submission.plain = plain
    else:
        return False

    session.add(submission)
    session.commit()

    return submission.id


# getRole: チャンネルに紐付けられているロールの Discord 上での ID を返す。
def getRole(channel_id):
    role = (
        session.query(Role)
        .filter(or_(Role.chat_tc == int(channel_id), Role.post_tc == int(channel_id)))
        .first()
    )
    if role:
        return str(role.id)
    else:
        return None


# getTc: ロールに帰属するテキストチャンネルの ID を返す
## type:
### chat: チャット用テキストチャンネル
### post: 提出用テキストチャンネル
def getTc(id, type):
    role = session.query(Role).filter(Role.id == int(id)).first()

    if role:
        if type == "chat":
            return role.chat_tc
        elif type == "post":
            return role.post_tc
        else:
            return None
    else:
        return None


# getCategory: テキスト チャンネルに帰属させるカテゴリーの ID を返す
## type:
### chat: チャット用カテゴリ
### post: 提出用カテゴリ
def getCategory(type):
    if type == "chat":
        config = session.query(Config).filter(Config.key == "chat_category").first()
    elif type == "post":
        config = session.query(Config).filter(Config.key == "post_category").first()
    elif type == "notify":
        config = session.query(Config).filter(Config.key == "notify_category").first()
    else:
        return None

    if config is None:
        return None
    else:
        return config.value


# getItemName: 提出先の ID から、提出先の名前を返す
def getItemName(id):
    item = session.query(Item).filter(Item.id == id).first()
    if item:
        return str(item.name)
    else:
        return None


# getSubmitAuthor: 提出 ID から、提出者を返す
def getSubmitAuthor(id):
    submit = session.query(Submission).filter(Submission.id == int(id)).first()
    if submit:
        return submit.author
    else:
        return None


# getSubmit: 提出 ID から、提出を返す
def getSubmit(id):
    submit = session.query(Submission).filter(Submission.id == int(id)).first()
    if submit:
        return submit
    else:
        return None


# getItemTarget: 提出先の ID から、提出先の対象者の Discord 上のロール ID を返す
def getItemTarget(id):
    item = session.query(Item).filter(Item.id == id).first()
    if item:
        return str(item.target)
    else:
        return None


# getChildRole: 親ロール ID から、帰属するロールを返す
def getChildRole(id):
    role = session.query(Role).filter(Role.parent_role == id).all()
    return role


# getItemFormat: 提出先の ID から、指示された提出先の形式を返す
def getItemFormat(id):
    item = session.query(Item).filter(Item.id == id).first()
    if item:
        if item.format == "file" or item.format == "plain":
            return item.format
        else:
            return None
    else:
        return None


# getItemLimit: 提出先の ID から、提出先の期限を datetime 型で返す
def getItemLimit(id):
    item = session.query(Item).filter(Item.id == id).first()
    if item:
        return item.limit
    else:
        return None


# getSubmitAuthorRole(id): 提出 ID から、その提出を行ったロールの ID を返す
def getSubmitAuthorRole(id):
    submit = session.query(Submission).filter(Submission.id == id).first()
    if submit:
        return submit.author_role
    else:
        return None


# isPostTc: 引数の Discord テキストチャンネルが提出用のチャンネルかを返す (True / False)
def isPostTc(post_tc):
    role = session.query(Role).filter(Role.post_tc == post_tc).first()
    return role


# getSubmitList(item_id, author_role): 提出先の ID と提出者のロール ID から、提出された項目のデータを返す
def getSubmitList(item_id, author_role):
    if author_role is None:
        submission = (
            session.query(Submission).filter(Submission.item_id == int(item_id)).all()
        )
    else:
        submission = (
            session.query(Submission)
            .filter(
                Submission.item_id == int(item_id),
                Submission.author_role == int(author_role),
            )
            .all()
        )
    return submission


# getParentRoleList(): ボットに登録されている親ロールのリストを返す
def getParentRoleList():
    parent_role = session.query(ParentRole).all()
    return parent_role

# getNotifyTc(role_id): 指定したロール ID の通知用テキストチャンネルを返す
def getNotifyTc(role_id):
    if isParentRole(role_id):
        parent_role_id = role_id
    else:
        parent_role_id = getParentRole(role_id)
    
    if parent_role_id is None:
        return None
    else:
        parent_role = session.query(ParentRole).filter(ParentRole.id == int(parent_role_id)).first()
        if parent_role is None:
            return None
        else:
            return parent_role.notify_tc
        

# addParentRole(id, type): 親ロールをボットに登録する
def addParentRole(id, type, notify_tc):
    exists = session.query(ParentRole).filter(ParentRole.id == id).first()
    if exists:
        return False
    else:
        parent_role = ParentRole()
        if str(id).isdigit():
            if type == "staff":
                parent_role.id = int(id)
                parent_role.type = "staff"
                parent_role.notify_tc = None
                session.add(parent_role)
                session.commit()
                return True
            elif type == "member":
                parent_role.id = int(id)
                parent_role.type = "member"
                parent_role.notify_tc = notify_tc
                session.add(parent_role)
                session.commit()
                return True
            else:
                return False
        else:
            return False


# delParentRole(id): 親ロールをボットから削除する
def delParentRole(role_id):
    exists = session.query(ParentRole).filter(ParentRole.id == role_id).first()
    if exists:
        session.delete(exists)
        session.commit()
        return True
    else:
        return False


# setParentRole(id, parent_role): 既にボットに登録されている子ロールの親ロールを更新する
def setParentRole(id, parent_role):
    role = session.query(Role).filter(Role.id == id).first()
    if role:
        role.parent_role = parent_role

        session.commit()
        return True
    else:
        return False


# isParentRole(id): 指定したロールが親ロールとしてボットに登録されているか返す
def isParentRole(id):
    if str(id).isdigit():
        parent_role = session.query(ParentRole).filter(ParentRole.id == int(id)).first()
        if parent_role:
            return True
        else:
            return False
    else:
        return False


# getParentRole(role_id): 指定したロールの親ロールを取得する
def getParentRole(role_id):
    if isParentRole(role_id):
        return role_id
    else:
        role = session.query(Role).filter(Role.id == int(role_id)).first()
        if role:
            return role.parent_role
        else:
            return None


# getUserParentRole(client, user_id): 指定したユーザの親ロールを返す
def getUserParentRole(message):
    member = message.guild.get_member(message.author.id)
    if member is None:
        return None
    else:
        parent_roles = []
        roles = []

        for parent_role in getParentRoleList():
            parent_roles.append(parent_role.id)

        for role in member.roles:
            roles.append(role.id)

        and_list = list(set(parent_roles) & set(roles))

        if len(and_list) == 0:
            return None
        else:
            return and_list[0]


# verifySubmit(id): 指定した提出を承認する
def verifySubmit(id):
    submit = session.query(Submission).filter(Submission.id == id).first()
    if submit is None:
        return None
    else:
        submit.verified = True
        session.commit()
        return True


# getRoles(): 登録されているすべての子ロールを返す
def getRoles():
    roles = session.query(Role).all()
    return roles

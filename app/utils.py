# 外部ライブラリ
import datetime
import dateutil
import discord
from parse import *
import pykakasi

# 内部関数
import database

# dtToStr: datetime 型の入力を、人間可読な str として返す (例: YYYY/MM/dd HH:mm:ss)
def dtToStr(dt):
    return dt.strftime("%Y/%-m/%-d %-H:%M:%S")


# roleIdToMention: Discord 上のロール ID をメンションのための str として返す
def roleIdToMention(role_id):
    return "<@&" + role_id + ">"


# mentionToRoleId: Discord のメンション文字列 (str) から ID 部分だけを抜き取って int で返す
def mentionToRoleId(mention):
    res = parse("<@&{}>", mention)
    if res:
        return int(res[0])
    else:
        return None


# roleIdToName: Discord のロール ID からロール名に変換する
def roleIdToName(role_id, guild):
    role = guild.get_role(int(role_id))
    if role is None:
        return None
    else:
        return role.name


# userIdToName: Discord のユーザー ID から名前に変換する
def userIdToName(client, user_id):
    user = client.get_user(int(user_id))
    if user is None:
        return None
    else:
        return user.name


# is_datetime: 与えられた str が日時として認識できるかを確認する。
def isDateTime(string, fuzzy=False):
    try:
        dateutil.parser.parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


# isStaff: 指定したユーザーがスタッフ用ロールを持っているかを True / False で返す
def isStaff(author, guild):
    staff_role = database.getStaffRole()
    if staff_role is None:
        return None
    else:
        role = discord.utils.get(guild.roles, id=int(staff_role))
        return role in author.roles


# isValidAsName: 新規作成する項目の名前として正しいかを True / False で返す
def isValidAsName(name):
    checkNotRole = parse("<@&{}>", name)
    checkNotMention = parse("<@{}>", name)
    checkNotChannel = parse("<#{}>", name)

    if checkNotRole or checkNotMention or checkNotChannel:
        return False
    else:
        return True


# convFileName(name): 日本語を含むファイル名をローマ字に変換する
def convFileName(name):
    name = name.replace("./data/posts/", "")
    kks = pykakasi.kakasi()
    converted = kks.convert(name)
    result = ""
    for item in converted:
        result += item["hepburn"]
    return result

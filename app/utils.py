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


# dtToStrFileName: datetime 型の入力を、人間可読な str として返す (例: YYYY-MM-dd_HH-mm-ss)
def dtToStrFileName(dt):
    return dt.strftime("%Y-%m-%d_%H-%M-%S")


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
    if str(role_id).isdigit():
        role = guild.get_role(int(role_id))
        if role is None:
            return "N/A"
        else:
            return role.name
    else:
        return "err"


# userIdToName: Discord のユーザー ID から名前に変換する
def userIdToName(guild, user_id):
    user = guild.get_member(int(user_id))
    if user is None:
        return None
    else:
        if user.nick is None:
            return user.name
        else:
            return user.nick


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


# isStaffRole(role_id): 指定したロールが委員会側のロールであるかを True / False で返す
def isStaffRole(role_id):
    for role in database.getParentRoleList():
        if role.id == role_id and role.type == "staff":
            return True

    return False


def toBinary(str_input):
    l, m = [], []
    for i in str_input:
        l.append(ord(i))
    for i in l:
        m.append(int(bin(i)[2:]))
    return m


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


def getUserRoles(guild, user_id):
    member = guild.get_member(user_id)
    member_role = guild.get_role(int(database.getMemberRole()))
    roles = []
    for role in member.roles:
        if role != guild.default_role:
            if role != member_role:
                roles.append(role)

    return roles


def getUserRolesName(guild, user_id):
    roles = getUserRoles(guild, user_id)
    role_name = []
    for role in roles:
        role_name.append(role.name)

    return role_name


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


def getUserRolesNameFmt(guild, user_id):
    role_name = getUserRolesName(guild, user_id)
    role_name_fmt = ""

    for index, role in enumerate(role_name):
        role_name_fmt += role
        if index + 1 < len(role_name):
            role_name_fmt += ", "

    return role_name_fmt

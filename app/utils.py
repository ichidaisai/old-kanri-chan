# 外部ライブラリ
import datetime
import dateutil
from parse import *

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
    return guild.get_role(int(role_id)).name


# is_datetime: 与えられた str が日時として認識できるかを確認する。
def isDateTime(string, fuzzy=False):
    try:
        dateutil.parser.parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


# isValidAsRoleName: 新規作成するロールの名前として正しいかを True / False で返す
def isValidAsRoleName(role_name):
    checkNotRole = parse("<@&{}>", role_name)
    checkNotMention = parse("<@{}>", role_name)
    checkNotChannel = parse("<#{}>", role_name)

    if checkNotRole or checkNotMention or checkNotChannel:
        return False
    else:
        return True

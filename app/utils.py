# 外部ライブラリ
import datetime
from parse import *

# dtToStr: datetime 型の入力を、人間可読な str として返す (例: YYYY/MM/dd HH:mm:ss)
def dtToStr(dt):
    return dt.strftime('%Y/%-m/%-d %-H:%M:%S')

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
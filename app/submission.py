# 外部ライブラリ
import discord
from parse import *
import datetime

# 内部関数
import database
import channel
import utils

async def addItem(message):
    response = parse("!add item {} {} {} {}", message.content)
    # コマンドの内容を精査する。
    if response:
        # 最初に、日付がパースできるかを確認する。
        parse_dt = parse("{}-{}-{}-{}-{}", response[1])
        if parse_dt: # 日付がパースできた
            dt = datetime.datetime(
                int(parse_dt[0]), # 年 (西暦)
                int(parse_dt[1]), # 月
                int(parse_dt[2]), # 日
                int(parse_dt[3]), # 時
                int(parse_dt[4]), # 分
                0 # 秒 = 0 (強制)
            )
            
            # 次に、ロール部分が本当にメンションかを精査する。
            role_id = utils.mentionToRoleId(response[2])
            if role_id is not None:
                    # 最後に、種類が file または plain で指定されていることを確認する。
                    if response[3] == "file" or response[3] == "plain":
                        result = database.addItem(response[0], dt, role_id, response[3])
                        # 種類を日本語に変換し、可読性を良くする
                        format_fd = ""
                        if response[3] == "file":
                            format_fd = "ファイル"
                        else:
                            format_fd = "プレーンテキスト"
                            
                        await message.channel.send(
                            "✅ 以下の提出物を登録しました: "
                            + "\n項目名: " + database.getItemName(result)
                            + "\n期限: " + utils.dtToStr(database.getItemLimit(result))
                            + "\n対象: " + utils.roleIdToMention(database.getItemTarget(result))
                            + "\n種類: " + format_fd
                            + "\n"
                            + "\n今までに登録した項目は、`!show item` で参照してください。"
                        )
                    else:
                        await message.channel.send("❌ 種類の指定方法が間違っています。`file` または `plain` を指定してください。")
                
            else:
                await message.channel.send("❌ ロールの指定方法が間違っています。コマンドをご確認ください。")

        else:
            await message.channel.send("❌ 日時の形式が間違っています。コマンドをご確認ください。")
        
    else:
        await message.channel.send(
            "❌ コマンドが不正です。\n"
            + "使用法: `!add item [名前] [期限] [対象] [種類]`\n"
            + "[名前]: 提出物の項目名を指定してください。\n"
            + "[期限]: 提出期限を `西暦-月-日-時-分` で指定してください。(例: `2022-04-19-18-00`)\n"
            + "[対象]: その提出物を提出するべきロールをメンションしてください。(例: `@サークルA`)"
            + "[種類]: 提出の形式を、ファイルの場合は `file`、テキストの場合は `plain` で指定します。"
        )

async def delItem(message):
    response = parse("!del item {}", message.content)
    if response:
        database.setChatTc(response[0], message.channel.id)
        await message.channel.send(
            "提出物 "
            + response[0]
            + " を削除しました。"
        )
    else:
        await message.channel.send("コマンドが不正です。")

async def showRole(message):
    response = parse("!show role", message.content)
    if response:
        await message.channel.send(
            str(
                database.showItem(
                        channel.showRole(message)
                    )
                )
            )
    else:
        await message.channel.send("コマンドが不正です。")

async def showItem(message):
    response = parse("!show item", message.content)
    if response:
        await message.channel.send(
            str(
                database.showItem(
                        channel.showRole(message)
                    )
                )
            )
    else:
        await message.channel.send("コマンドが不正です。")
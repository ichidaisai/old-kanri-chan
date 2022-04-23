# 外部ライブラリ
import discord
from parse import *
import datetime
from dateutil import tz
import asyncio

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
        if parse_dt:  # 日付がパースできた
            dt = datetime.datetime(
                int(parse_dt[0]),  # 年 (西暦)
                int(parse_dt[1]),  # 月
                int(parse_dt[2]),  # 日
                int(parse_dt[3]),  # 時
                int(parse_dt[4]),  # 分
                0,  # 秒 = 0 (強制)
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
                        + "\n項目名: "
                        + database.getItemName(result)
                        + "\n期限: "
                        + utils.dtToStr(database.getItemLimit(result))
                        + "\n対象: "
                        + utils.roleIdToMention(database.getItemTarget(result))
                        + "\n種類: "
                        + format_fd
                        + "\n"
                        + "\n今までに登録した項目は、`!show item` で参照してください。"
                    )
                else:
                    await message.channel.send(
                        "❌ 種類の指定方法が間違っています。`file` または `plain` を指定してください。"
                    )

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
            + "[対象]: その提出物を提出するべきロールをメンションしてください。(例: `@サークルA`)\n"
            + "[種類]: 提出の形式を、ファイルの場合は `file`、テキストの場合は `plain` で指定します。"
        )


async def delItem(message):
    response = parse("!del item {}", message.content)
    if response:
        result = database.delItem(response[0])
        if result is False:
            await message.channel.send("⚠ 提出物が見つかりません。ID をご確認ください。")
        else:
            await message.channel.send("✅ 提出物 " + response[0] + " を削除しました。")
    else:
        await message.channel.send("❌ コマンドが不正です。")

## TODO: 提出したとき、そのアイテムがロールに属しているかを確認する
async def showItem(message):
    result = database.getRole(message.channel.id)
    
    if result is None:
        await message.channel.send("⚠ このチャンネルはボットに認識されていません。")
    else:
        await message.channel.send(
            "**"
            + utils.roleIdToName(
                int(database.getRole(message.channel.id)), message.guild
            )
            + "** に提出が指示された提出物は以下の通りです: \n"
            + returnItem(message)
        )

async def submitItem(client, message):
    if returnItem(message) == "今のところ、提出を指示されている項目はありません。":
        await message.channel.send(
        "ファイルを検出しましたが、あなたが提出するべき項目は登録されていません。\n"
        + "委員会が提出物を登録するまで、しばらくお待ちください。"
        )
    else:
        channel = message.channel
        
        await channel.send(
            "ファイルを検出しました。\n"
            + "どの提出物を提出しようとしていますか？\n"
            + returnItem(message)
            + "\n提出したい項目の ID を、このチャンネルで発言してください。"
            )
        
        def check(m):
            return m.channel == channel
        
        try:
            msg = await client.wait_for('message', check=check, timeout=30)
            
        except asyncio.TimeoutError:
            await channel.send("⚠ タイムアウトしました。もう一度、ファイルのアップロードからやり直してください。")
        else:
            if database.getItemName(msg.content) is False or database.getItemTarget(msg.content) != database.getRole(message.channel.id):
                await channel.send("⚠ 指定された ID は間違っています。もう一度、ファイルのアップロードからやり直してください。")
            else:
                item_count = 0
                for attachment in message.attachments:
                    # ファイル名を決定
                    JST = tz.gettz('Asia/Tokyo')
                    dt_now = datetime.datetime.now(JST)
                    dt_now_fmt = dt_now.strftime("%Y-%M-Z%")
                    filename = dt_now.strftime(
                        # アウトプット 例: `2022-05-01_20-30-21_サークルA_提出物1.docx`
                        "%Y-%m-%d_%H-%M-%S_" # タイムスタンプ
                        + utils.roleIdToName(database.getRole(message.channel.id), message.guild) # ロール名
                        + "_"
                        + attachment.filename
                    )
                    await attachment.save(filename)
                    item_count += 1
                    
                await channel.send(
                    "✅ 提出物 "
                    + "**" 
                    + database.getItemName(msg.content) 
                    + "** を提出しました。("
                    + str(item_count) 
                    + "件のファイル)"
                    )

def returnItem(message):
    items = ""
    for item in database.showItem(database.getRole(message.channel.id)):
        items += "\n"
        items += "提出物 ID: " + str(item.id) + "\n"
        items += "項目名: " + item.name + "\n"
        items += "提出期限: " + utils.dtToStr(item.limit) + "\n"
        if item.verified == True:
            items += "委員会からの確認: **済**\n"
        else:
            items += "委員会からの確認: **未**\n"
        if item.format == "file":
            items += "提出形式: ファイル\n"
        elif item.format == "plain":
            items += "提出形式: プレーンテキスト\n"
        else:
            items += "提出形式: 不明。委員会までお問い合わせください。\n"
    if items == "":
        items += "今のところ、提出を指示されている項目はありません。"
    return items
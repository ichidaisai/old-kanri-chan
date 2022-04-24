# 外部ライブラリ
import discord
from parse import *
import datetime
import dateutil.parser
import asyncio

# 内部関数
import database
import channel
import utils

# 提出物の登録 (対話方式)
async def addItemInteract(client, message):
    # 提出物の名前を読み込む
    await message.channel.send("📛 提出物の名前は何にしますか？")

    def check(m):
        return m.channel == message.channel and m.author == message.author

    try:
        m_item_name = await client.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        await message.channel.send("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
    else:
        item_name = m_item_name.content
        await message.channel.send("✅ 提出物の名前を **" + item_name + "** にしました。")

        # 提出物の期限を読み込む
        await message.channel.send(
            "⏰ 提出物の期限はいつにしますか？\n"
            + "入力例: 2022年4月1日 21時30分 としたい場合は、`2022/4/1 21:30` と入力します。\n"
        )

        try:
            m_item_limit = await client.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
            await message.channel.send("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
        else:
            if utils.isDateTime(m_item_limit.content):
                item_limit = dateutil.parser.parse(m_item_limit.content)
                await message.channel.send(
                    "✅ 提出物の期限を `" + utils.dtToStr(item_limit) + "` にしました。"
                )

                # 提出物の対象を読み込む
                await message.channel.send(
                    "👤 提出物の対象者はいつにしますか？\n" + "Discord のメンション機能を使用して、ロールを指定してください。"
                )
                try:
                    m_item_target = await client.wait_for(
                        "message", check=check, timeout=30
                    )
                except asyncio.TimeoutError:
                    await message.channel.send("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
                else:
                    role_id = utils.mentionToRoleId(m_item_target.content)
                    if role_id is not None:
                        item_target = role_id
                        await message.channel.send(
                            "✅ 提出物の対象者を **"
                            + utils.roleIdToName(role_id, message.guild)
                            + "** にしました。"
                        )

                        # 提出物の形式を読み込む
                        await message.channel.send(
                            "💾 提出物の形式はどちらにしますか？\n"
                            + "ファイル形式の場合は `file`、プレーンテキスト形式の場合は `plain` と返信してください。"
                        )
                        try:
                            m_item_format = await client.wait_for(
                                "message", check=check, timeout=30
                            )
                        except asyncio.TimeoutError:
                            await message.channel.send(
                                "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。"
                            )
                        else:
                            if (
                                m_item_format.content == "file"
                                or m_item_format.content == "plain"
                            ):
                                item_format = m_item_format.content
                                # 種類を日本語に変換し、可読性を良くする
                                format_fmt = ""
                                if item_format == "file":
                                    format_fmt = "📄 ファイル"
                                else:
                                    format_fmt = "📜 プレーンテキスト"

                                await message.channel.send(
                                    "✅ 提出物の形式を **" + format_fmt + "** にしました。"
                                )

                                # データベースにコミット
                                result = database.addItem(
                                    item_name, item_limit, item_target, item_format
                                )
                                await message.channel.send(
                                    "✅ 以下の提出物を登録しました: "
                                    + "\n📛 項目名: "
                                    + database.getItemName(result)
                                    + "\n⏰ 期限: "
                                    + utils.dtToStr(database.getItemLimit(result))
                                    + "\n👤 対象: "
                                    + utils.roleIdToName(
                                        database.getItemTarget(result), message.guild
                                    )
                                    + "\n💾 種類: "
                                    + format_fmt
                                    + "\n"
                                    + "\n今までに登録した項目は、`!show item` で参照してください。"
                                )
                            else:
                                await message.channel.send(
                                    "⚠ 提出形式が正確に指定されていません。\n"
                                    + "`file` か `plain` のどちらかを返信してください。\n"
                                    + "もう一度、最初から操作をやり直してください。"
                                )

                    else:
                        await message.channel.send(
                            "⚠ 対象者が正確に指定されていません。\n"
                            + "Discord のメンション機能を使用して、ロールを指定してください。\n"
                            + "もう一度、最初から操作をやり直してください。"
                        )

            else:
                await message.channel.send(
                    "⚠ 指定された期限をうまく解釈できませんでした。\n"
                    + "入力例: 2022年4月1日 21時30分 としたい場合は、`2022/4/1 21:30` と入力します。\n"
                    + "もう一度、最初から操作をやり直してください。"
                )


# 提出物の登録
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
                    format_fmt = ""
                    if response[3] == "file":
                        format_fmt = "📄 ファイル"
                    else:
                        format_fmt = "📜 プレーンテキスト"

                    await message.channel.send(
                        "✅ 以下の提出物を登録しました: "
                        + "\n📛 項目名: "
                        + database.getItemName(result)
                        + "\n⏰ 期限: "
                        + utils.dtToStr(database.getItemLimit(result))
                        + "\n👤 対象: "
                        + utils.roleIdToName(
                            database.getItemTarget(result), message.guild
                        )
                        + "\n💾 種類: "
                        + format_fmt
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


# 登録された提出物の削除
async def delItem(message):
    response = parse("!del item {}", message.content)
    if response:
        item_name = database.getItemName(response[0])
        result = database.delItem(response[0])
        if result is False:
            await message.channel.send("⚠ 提出物が見つかりません。ID をご確認ください。")
        else:
            await message.channel.send("✅ 提出物 " + item_name + " を削除しました。")
    else:
        await message.channel.send("❌ コマンドが不正です。")


# 登録された提出物を表示, 特定のロールに紐付いた提出物のみ表示する
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
            + returnItem(message, "all")
        )


# 提出物を提出する
async def submitFileItem(client, message):
    if returnItem(message, "file") == "今のところ、提出を指示されている項目はありません。":
        await message.channel.send(
            "⚠ ファイルを検出しましたが、あなたが提出するべき項目は登録されていません。\n" + "委員会が提出物を登録するまで、しばらくお待ちください。"
        )
    else:
        channel = message.channel

        await channel.send(
            "❗ ファイルを検出しました。\n"
            + "どの提出物を提出しようとしていますか？\n"
            + returnItem(message, "file")
            + "\n提出したい項目の ID を、このチャンネルで発言してください。"
        )

        def check(m):
            return m.channel == channel and m.author == message.author

        try:
            msg = await client.wait_for("message", check=check, timeout=30)

        except asyncio.TimeoutError:
            await channel.send("⚠ タイムアウトしました。もう一度、ファイルのアップロードからやり直してください。")
        else:
            if database.getItemName(msg.content) is False:
                await channel.send("⚠ 指定された ID は間違っています。もう一度、ファイルのアップロードからやり直してください。")
            elif database.getItemTarget(msg.content) != database.getRole(
                message.channel.id
            ):
                print("getItemTarget: " + str(database.getItemTarget(msg.content)))
                print("\n")
                print(
                    "database.getRole(message.channel.id): "
                    + database.getRole(message.channel.id)
                )
                await channel.send(
                    "⚠ その提出物はあなたに割り当てられていません。もう一度、ファイルのアップロードからやり直してください。"
                )
            else:
                if database.getItemFormat(msg.content) == "file":
                    item_count = 0
                    for attachment in message.attachments:
                        # ファイル名を決定
                        JST = dateutil.tz.gettz("Asia/Tokyo")
                        dt_now = datetime.datetime.now(JST)
                        filename = dt_now.strftime(
                            # アウトプット 例: `2022-05-01_20-30-21_サークルA_申込用紙1_提出物1.docx`
                            # ファイルは `posts/` 以下に保存される。
                            "posts/"
                            + "%Y-%m-%d_%H-%M-%S_"  # タイムスタンプ
                            + utils.roleIdToName(
                                database.getRole(message.channel.id), message.guild
                            )  # ロール名
                            + "_"
                            + database.getItemName(msg.content)
                            + "_"
                            + attachment.filename
                        )
                        await attachment.save(filename)
                        item_count += 1
                        database.addSubmit(
                            msg.content,  # item_id
                            dt_now,  # datetime
                            filename,  # filename
                            None,  # plain, file なので NULL
                            database.getItemTarget(msg.content),  # target
                            "file",  # format
                        )

                    await channel.send(
                        "✅ 提出物 "
                        + "**"
                        + database.getItemName(msg.content)
                        + "** を提出しました。("
                        + str(item_count)
                        + "件のファイル)"
                    )
                elif database.getItemFormat(msg.content) == "plain":
                    await channel.send(
                        "⚠ 提出物 "
                        + "**"
                        + database.getItemName(msg.content)
                        + "** はファイルではなくテキストで提出してください。"
                    )
                else:
                    await channel.send("⚠ 処理中になんらかの問題が発生しました。")


# 提出物の一覧を整形して str として返す
## format:
## all: すべての提出形式の提出物を返す
## file: ファイル形式の提出物を返す
## plain: プレーンテキスト形式の提出物を返す
def returnItem(message, format):
    items = ""
    for item in database.showItem(database.getRole(message.channel.id), format):
        items += "\n"
        items += "🆔 提出物 ID: " + str(item.id) + "\n"
        items += "📛 項目名: " + item.name + "\n"
        items += "⏰ 提出期限: `" + utils.dtToStr(item.limit) + "`\n"
        if item.format == "file":
            items += "💾 提出形式: 📄 ファイル\n"
        elif item.format == "plain":
            items += "💾 提出形式: 📜 プレーンテキスト\n"
        else:
            items += "💾 提出形式: 不明。委員会までお問い合わせください。\n"
    if items == "":
        items += "今のところ、提出を指示されている項目はありません。"
    return items

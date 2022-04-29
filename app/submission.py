# 外部ライブラリ
import discord
from parse import *
import datetime
import asyncio
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
        if utils.isValidAsName(item_name) is False:
            await message.channel.send("⚠ 提出物の名前として正しくありません。もう一度、最初から操作をやり直してください。")
        else:
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
                        "👤 提出物の対象者はいつにしますか？\n" + "__Discord のメンション機能を使用して、__ロールを指定してください。"
                    )
                    try:
                        m_item_target = await client.wait_for(
                            "message", check=check, timeout=30
                        )
                    except asyncio.TimeoutError:
                        await message.channel.send(
                            "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。"
                        )
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
                                    
                                    item_handler = database.getUserParentRole(message)

                                    # データベースにコミット
                                    result = database.addItem(
                                        item_name, item_limit, item_target, item_handler, item_format
                                    )
                                    await message.channel.send(
                                        "✅ 以下の提出物を登録しました: "
                                        + "\n📛 項目名: "
                                        + database.getItemName(result)
                                        + "\n⏰ 期限: "
                                        + utils.dtToStr(database.getItemLimit(result))
                                        + "\n👤 対象: "
                                        + utils.roleIdToName(
                                            database.getItemTarget(result),
                                            message.guild,
                                        )
                                        + "\n💾 種類: "
                                        + format_fmt
                                        + "\n"
                                        + "\n今までに登録した項目は、`!item list` で参照してください。"
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
                                + "__Discord のメンション機能を使用して、__ロールを指定してください。\n"
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
                        + "\n今までに登録した項目は、`!item list` で参照してください。"
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
    response = parse("!item delete {}", message.content)
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
async def listItem(client, message):
    result = database.getRole(message.channel.id)

    if result is None:
        await message.channel.send(
            ":mage: どのロールの提出物を確認しますか？\n__Discord のメンション機能を使用して、__ロールを指定してください。"
        )

        def check(m):
            return m.channel == message.channel and m.author == message.author

        try:
            msg = await client.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
            await message.channel.send("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
        else:
            target_id = utils.mentionToRoleId(msg.content)

            if target_id is None:
                await message.channel.send(
                    "⚠ ロールの指定方法が間違っています。Discord のメンション機能を用いて、ロールを指定してください。"
                )
            else:
                target = message.guild.get_role(int(target_id))

                if target is None:
                    await message.channel.send(
                        "⚠ 対象のロールが見つかりませんでした。指定しているロールが本当に正しいか、再確認してください。"
                    )
                else:
                    if database.getTc(target.id, "post") is None and database.isParentRole(target.id) is False:
                        await message.channel.send(
                            "⚠ ロール **" + target.name + "** は、提出を指示する先のロールとしては登録されていません。"
                        )
                    else:
                        await message.channel.send(
                            "**"
                            + utils.roleIdToName(target.id, message.guild)
                            + "** に提出が指示された提出物は以下の通りです: \n"
                            + returnItemByRoleId(target.id, "all")
                        )
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
    if not message.author.bot:
        if returnItem(message, "file") == "今のところ、提出を指示されている項目はありません。":
            print("parent role: " + str(database.getParentRole(database.getRole(message.channel.id))))
            await message.channel.send(
                "⚠ ファイルを検出しましたが、あなたが提出するべき項目は登録されていません。\n"
                + "委員会が提出物を登録するまで、しばらくお待ちください。"
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
                    await channel.send(
                        "⚠ 指定された ID は間違っています。もう一度、ファイルのアップロードからやり直してください。"
                    )
                else:
                    target = database.getItemTarget(msg.content)
                    role_id = database.getRole(message.channel.id)
                    parent_role_id = database.getParentRole(database.getRole(message.channel.id))
                    
                    # 特定の子ロールだけに指示された提出物
                    if target == role_id or target == str(parent_role_id):
                        if database.getItemFormat(msg.content) == "file":
                            item_count = 0
                            for attachment in message.attachments:
                                # ファイル名を決定
                                JST = dateutil.tz.gettz("Asia/Tokyo")
                                dt_now = datetime.datetime.now(JST)
                                filename = attachment.filename
                                path = dt_now.strftime(
                                    # アウトプット 例: `2022-05-01_20-30-21_サークルA_申込用紙1_提出物1.docx`
                                    # ファイルは `posts/` 以下に保存される。
                                    "./data/posts/"
                                    + "%Y-%m-%d_%H-%M-%S_"  # タイムスタンプ
                                    + utils.roleIdToName(
                                        database.getRole(message.channel.id), message.guild
                                    )  # ロール名
                                    + "_"
                                    + database.getItemName(msg.content)
                                    + "_"
                                    + attachment.filename
                                )
                                await attachment.save(path)
                                item_count += 1
                                database.addSubmit(
                                    msg.content,  # item_id
                                    dt_now,  # datetime
                                    filename,  # filename
                                    path,  # path, サーバー上のファイルの場所
                                    None,  # plain, file なので NULL
                                    message.author.id,  # author, 提出者の Discord 内部 ID
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
                    else:
                        await channel.send(
                            "⚠ その提出物はあなたに割り当てられていません。もう一度、ファイルのアップロードからやり直してください。"
                        )


# 提出物の一覧を整形して str として返す (テキストチャンネルの ID で絞り込む)
## format:
## all: すべての提出形式の提出物を返す
## file: ファイル形式の提出物を返す
## plain: プレーンテキスト形式の提出物を返す
def returnItem(message, format):
    items = ""
    # 特定ロールのみに指示された提出物
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
    # 親ロールに指示された提出物
    for item in database.showItem(database.getParentRole(database.getRole(message.channel.id)), format):
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


# 提出物の一覧を整形して str として返す (Discord 上のロール ID で絞り込む)
## format:
## all: すべての提出形式の提出物を返す
## file: ファイル形式の提出物を返す
## plain: プレーンテキスト形式の提出物を返す
def returnItemByRoleId(role_id, format):
    items = ""
    for item in database.showItem(role_id, format):
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
    for item in database.showItem(database.getParentRole(role_id), format):
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


async def listSubmitInteract(client, message):
    result = database.getRole(message.channel.id)

    def check(m):
        return m.channel == message.channel and m.author == message.author

    if result is None:
        await message.channel.send(
            ":man_mage: どのロールが提出した提出物を見ますか？\n" + "Discord のメンション機能を用いて、ロールを指定してください。"
        )

        try:
            msg_role = await client.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
            await message.channel.send("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
        else:
            target_id = utils.mentionToRoleId(msg_role.content)

            if target_id is None:
                await message.channel.send(
                    "⚠ ロールの指定方法が間違っています。Discord のメンション機能を用いて、ロールを指定してください。"
                )
            else:
                target = message.guild.get_role(int(target_id))

                if target is None:
                    await message.channel.send(
                        "⚠ 対象のロールが見つかりませんでした。指定しているロールが本当に正しいか、再確認してください。"
                    )
                else:
                    if database.getTc(target.id, "post") is None:
                        await message.channel.send(
                            "⚠ ロール **" + target.name + "** は、提出を指示する先のロールとしては登録されていません。"
                        )
                    else:
                        await message.channel.send(
                            "**"
                            + utils.roleIdToName(target.id, message.guild)
                            + "** に提出が指示された提出物は以下の通りです。\n"
                            + "履歴を閲覧したい項目を選んでください。"
                            + returnItemByRoleId(target.id, "all")
                        )
                        try:
                            msg_item_id = await client.wait_for(
                                "message", check=check, timeout=30
                            )
                        except asyncio.TimeoutError:
                            await message.channel.send(
                                "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。"
                            )
                        else:
                            if msg_item_id.content.isdigit():
                                if database.getItemLimit(msg_item_id.content) is None:
                                    await message.channel.send(
                                        "⚠ 指定された ID **"
                                        + msg_item_id.content
                                        + "** 持つ提出物が見つかりませんでした。"
                                    )
                                else:
                                    item_id = msg_item_id.content

                                    submit_list = database.getSubmitList(item_id)
                                    list_fmt = formatSubmitList(
                                        client, submit_list, "all"
                                    )

                                    await message.channel.send(
                                        ":information_source: 以下が提出物 **"
                                        + database.getItemName(item_id)
                                        + "** (対象: "
                                        + database.getItemTarget(item_id)
                                        + ") の提出履歴です。\n"
                                        + list_fmt
                                    )
                            else:
                                await message.channel.send(
                                    "⚠ 番号で提出物 ID を指定してください。もう一度、最初から操作をやり直してください。"
                                )
    else:
        await message.channel.send(
            "**"
            + utils.roleIdToName(
                int(database.getRole(message.channel.id)), message.guild
            )
            + "** に提出が指示された提出物は以下の通りです。 \n"
            + "履歴を閲覧したい項目を選んでください: \n"
            + returnItem(message, "all")
        )
        try:
            msg_item_id = await client.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
            await message.channel.send("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
        else:
            if msg_item_id.content.isdigit():
                if database.getItemLimit(msg_item_id.content) is None:
                    await message.channel.send(
                        "⚠ 指定された ID **" + msg_item_id.content + "** 持つ提出物が見つかりませんでした。"
                    )
                else:
                    item_id = msg_item_id.content

                    submit_list = database.getSubmitList(item_id)
                    list_fmt = formatSubmitList(client, submit_list, "all")

                    await message.channel.send(
                        ":information_source: 以下が提出物 **"
                        + database.getItemName(item_id)
                        + "** (対象: "
                        + utils.roleIdToName(
                            database.getItemTarget(item_id), message.guild
                        )
                        + ") の提出履歴です。\n\n"
                        + list_fmt
                    )
            else:
                await message.channel.send(
                    "⚠ 番号で提出物 ID を指定してください。もう一度、最初から操作をやり直してください。"
                )


async def getSubmitInteract(client, message):
    result = database.getRole(message.channel.id)

    def check(m):
        return m.channel == message.channel and m.author == message.author

    if result is None:
        await message.channel.send(
            ":man_mage: どのロールが提出した提出物をダウンロードしますか？\n"
            + "Discord のメンション機能を用いて、ロールを指定してください。"
        )

        try:
            msg_role = await client.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
            await message.channel.send("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
        else:
            target_id = utils.mentionToRoleId(msg_role.content)

            if target_id is None:
                await message.channel.send(
                    "⚠ ロールの指定方法が間違っています。Discord のメンション機能を用いて、ロールを指定してください。"
                )
            else:
                target = message.guild.get_role(int(target_id))

                if target is None:
                    await message.channel.send(
                        "⚠ 対象のロールが見つかりませんでした。指定しているロールが本当に正しいか、再確認してください。"
                    )
                else:
                    if database.getTc(target.id, "post") is None:
                        await message.channel.send(
                            "⚠ ロール **" + target.name + "** は、提出を指示する先のロールとしては登録されていません。"
                        )
                    else:
                        await message.channel.send(
                            "**"
                            + utils.roleIdToName(target.id, message.guild)
                            + "** に提出が指示された提出物は以下の通りです。\n"
                            + "ダウンロードしたい項目を選んでください。"
                            + returnItemByRoleId(target.id, "all")
                        )
                        try:
                            msg_item_id = await client.wait_for(
                                "message", check=check, timeout=30
                            )
                        except asyncio.TimeoutError:
                            await message.channel.send(
                                "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。"
                            )
                        else:
                            if msg_item_id.content.isdigit():
                                if database.getItemLimit(msg_item_id.content) is None:
                                    await message.channel.send(
                                        "⚠ 指定された ID **"
                                        + msg_item_id.content
                                        + "** 持つ提出物が見つかりませんでした。"
                                    )
                                else:
                                    item_id = msg_item_id.content

                                    submit_list = database.getSubmitList(item_id)
                                    list_fmt = formatSubmitList(
                                        client, submit_list, "file"
                                    )

                                    await message.channel.send(
                                        ":information_source: 以下が提出物 **"
                                        + database.getItemName(item_id)
                                        + "** (対象: "
                                        + database.getItemTarget(item_id)
                                        + ") の提出履歴です。\n"
                                        + "ダウンロードしたいファイルを選んでください。\n"
                                        + list_fmt
                                    )

                                    try:
                                        msg_submit_id = await client.wait_for(
                                            "message", check=check, timeout=30
                                        )
                                    except asyncio.TimeoutError:
                                        await message.channel.send(
                                            "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。"
                                        )
                                    else:
                                        if (
                                            database.getSubmitAuthor(
                                                msg_submit_id.content
                                            )
                                            is None
                                        ):
                                            await message.channel.send(
                                                "⚠ 提出 ID が間違っています。もう一度、最初から操作をやり直してください。"
                                            )
                                        else:
                                            await message.channel.send(
                                                "✅ 以下の提出を送信します: \n\n"
                                                + formatSubmit(
                                                    client,
                                                    database.getSubmit(
                                                        msg_submit_id.content
                                                    ),
                                                ),
                                                file=discord.File(
                                                    database.getSubmit(
                                                        msg_submit_id.content
                                                    ).path
                                                ),
                                            )

                            else:
                                await message.channel.send(
                                    "⚠ 番号で提出物 ID を指定してください。もう一度、最初から操作をやり直してください。"
                                )
    else:
        await message.channel.send(
            "**"
            + utils.roleIdToName(
                int(database.getRole(message.channel.id)), message.guild
            )
            + "** に提出が指示された提出物は以下の通りです。 \n"
            + "ダウンロードしたい項目を選んでください: \n\n"
            + returnItem(message, "all")
        )
        try:
            msg_item_id = await client.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
            await message.channel.send("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
        else:
            if msg_item_id.content.isdigit():
                if database.getItemLimit(msg_item_id.content) is None:
                    await message.channel.send(
                        "⚠ 指定された ID **" + msg_item_id.content + "** 持つ提出物が見つかりませんでした。"
                    )
                else:
                    item_id = msg_item_id.content

                    submit_list = database.getSubmitList(item_id)
                    list_fmt = formatSubmitList(client, submit_list, "file")

                    await message.channel.send(
                        ":information_source: 以下が提出物 **"
                        + database.getItemName(item_id)
                        + "** (対象: "
                        + utils.roleIdToName(
                            database.getItemTarget(item_id), message.guild
                        )
                        + ") の提出履歴です。\n"
                        + "ダウンロードしたいファイルを選んでください。\n\n"
                        + list_fmt
                    )
                    try:
                        msg_submit_id = await client.wait_for(
                            "message", check=check, timeout=30
                        )
                    except asyncio.TimeoutError:
                        await message.channel.send(
                            "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。"
                        )
                    else:
                        if database.getSubmitAuthor(msg_submit_id.content) is None:
                            await message.channel.send(
                                "⚠ 提出 ID が間違っています。もう一度、最初から操作をやり直してください。"
                            )
                        else:
                            await message.channel.send(
                                "✅ 以下の提出を送信します: \n\n"
                                + formatSubmit(
                                    client, database.getSubmit(msg_submit_id.content)
                                ),
                                file=discord.File(
                                    database.getSubmit(msg_submit_id.content).path
                                ),
                            )
            else:
                await message.channel.send(
                    "⚠ 番号で提出物 ID を指定してください。もう一度、最初から操作をやり直してください。"
                )


def formatSubmit(client, submit):
    fmt = ""
    fmt += "🆔 提出 ID: " + str(submit.id) + "\n"
    fmt += "⏰ 提出日時: `" + utils.dtToStr(submit.datetime) + "`\n"
    if submit.format == "file":
        fmt += "📛 ファイル名: `" + submit.filename + "`\n"
    elif submit.format == "plain":
        fmt += "📝 内容: " + submit.plain + "\n"
    fmt += (
        ":man_construction_worker: 提出者: "
        + utils.userIdToName(client, submit.author)
        + "\n"
    )
    if submit.verified:
        fmt += "✅ 委員会からの承認: **済**\n"
    else:
        fmt += "✅ 委員会からの承認: **未**\n"
    fmt += "\n"

    return fmt


def formatSubmitList(client, submit_list, format):
    list_fmt = ""

    if len(submit_list) == 0:
        list_fmt += "まだ、この項目に対して何も提出されていません。"
    else:
        for submit in submit_list:
            if format == "all":
                list_fmt += "🆔 提出 ID: " + str(submit.id) + "\n"
                list_fmt += "⏰ 提出日時: `" + utils.dtToStr(submit.datetime) + "`\n"
                if submit.format == "file":
                    list_fmt += "📛 ファイル名: `" + submit.filename + "`\n"
                elif submit.format == "plain":
                    list_fmt += "📝 内容: " + submit.plain + "\n"
                list_fmt += (
                    ":man_construction_worker: 提出者: "
                    + utils.userIdToName(client, submit.author)
                    + "\n"
                )
                if submit.verified:
                    list_fmt += "✅ 委員会からの承認: **済**\n"
                else:
                    list_fmt += "✅ 委員会からの承認: **未**\n"
                list_fmt += "\n"
            elif format == "file":
                if submit.format == "file":
                    list_fmt += "🆔 提出 ID: " + str(submit.id) + "\n"
                    list_fmt += "⏰ 提出日時: `" + utils.dtToStr(submit.datetime) + "`\n"
                    list_fmt += "📛 ファイル名: `" + submit.filename + "`\n"
                    list_fmt += (
                        ":man_construction_worker: 提出者: "
                        + utils.userIdToName(client, submit.author)
                        + "\n"
                    )
                    if submit.verified:
                        list_fmt += "✅ 委員会からの承認: **済**\n"
                    else:
                        list_fmt += "✅ 委員会からの承認: **未**\n"
                    list_fmt += "\n"
            elif format == "plain":
                list_fmt += "🆔 提出 ID: " + str(submit.id) + "\n"
                list_fmt += "⏰ 提出日時: `" + utils.dtToStr(submit.datetime) + "`\n"
                list_fmt += "📝 内容: " + submit.plain + "\n"
                list_fmt += (
                    ":man_construction_worker: 提出者: "
                    + utils.userIdToName(client, submit.author)
                    + "\n"
                )
                if submit.verified:
                    list_fmt += "✅ 委員会からの承認: **済**\n"
                else:
                    list_fmt += "✅ 委員会からの承認: **未**\n"
                list_fmt += "\n"
            else:
                list_fmt += ""

    return list_fmt

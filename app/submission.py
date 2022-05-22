# 外部ライブラリ
import discord
from parse import *
import datetime
import asyncio
import dateutil.parser
import unicodedata
import pandas as pd
import os

# 内部関数
import database
import channel
import utils


# 提出先の登録 (対話方式)
async def addItemInteract(client, message):
    if database.getUserParentRole(message) is None:
        await message.channel.send(
            "⚠ あなたが持つ親ロールがまだボットに認識されていないか、または親ロールを何も持っていないため操作を続行できません。",
            reference=message,
        )
    else:
        if utils.isStaff(message.author, message.guild):
            # 提出先の名前を読み込む
            msg_ask_item_name = await message.channel.send(
                "📛 提出先の名前は何にしますか？", reference=message
            )

            def check(m):
                return m.channel == message.channel and m.author == message.author

            try:
                m_item_name = await client.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                await message.channel.send(
                    "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", reference=msg_ask_item_name
                )
            else:
                item_name = m_item_name.content
                if utils.isValidAsName(item_name) is False:
                    await message.channel.send(
                        "⚠ 提出先の名前として正しくありません。もう一度、最初から操作をやり直してください。",
                        reference=m_item_name,
                    )
                else:
                    msg_done_item_name = await message.channel.send(
                        "✅ 提出先の名前を **" + item_name + "** にしました。", reference=m_item_name
                    )

                    # 提出先の期限を読み込む
                    msg_ask_limit = await message.channel.send(
                        "⏰ 提出期限はいつにしますか？\n"
                        + "入力例: 2022年4月1日 21時30分 としたい場合は、`2022/4/1 21:30` と入力します。\n",
                        reference=msg_done_item_name,
                    )

                    try:
                        m_item_limit = await client.wait_for(
                            "message", check=check, timeout=60
                        )
                    except asyncio.TimeoutError:
                        await message.channel.send(
                            "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。",
                            reference=msg_ask_limit,
                        )
                    else:
                        if utils.isDateTime(m_item_limit.content):
                            item_limit = dateutil.parser.parse(m_item_limit.content)
                            if item_limit < datetime.datetime.now():
                                await message.channel.send(
                                    "⚠ 提出期限が過去に設定されています。\n" "もう一度、最初からやり直してください。",
                                    reference=m_item_limit,
                                )
                            else:
                                msg_done_limit = await message.channel.send(
                                    "✅ 提出期限を `" + utils.dtToStr(item_limit) + "` にしました。"
                                )

                                # 提出先の対象を読み込む
                                msg_ask_role = await message.channel.send(
                                    "👤 対象者はどのロールにしますか？\n"
                                    + "__Discord のメンション機能を使用して、__ロールを指定してください。",
                                    reference=msg_done_limit,
                                )
                                try:
                                    m_item_target = await client.wait_for(
                                        "message", check=check, timeout=60
                                    )
                                except asyncio.TimeoutError:
                                    await message.channel.send(
                                        "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。",
                                        reference=msg_ask_role,
                                    )
                                else:
                                    role_id = utils.mentionToRoleId(
                                        m_item_target.content
                                    )
                                    if role_id is not None:
                                        if utils.isStaffRole(role_id):
                                            await message.channel.send(
                                                "⚠ 指定したロールは、提出を指示する先のロールとしては登録されていません。\n"
                                                + "委員会サイドのロールを指定している場合は、そのようなことはできません。\n"
                                                + "ここでは、出店者側のロールを指定するようにしてください。\n"
                                                + "もう一度、最初から操作をやり直してください。",
                                                reference=m_item_target,
                                            )
                                        else:
                                            item_target = role_id
                                            msg_done_target = (
                                                await message.channel.send(
                                                    "✅ 提出先の対象者を **"
                                                    + utils.roleIdToName(
                                                        role_id, message.guild
                                                    )
                                                    + "** にしました。",
                                                    reference=m_item_target,
                                                )
                                            )

                                            # 提出先の形式を読み込む
                                            msg_ask_format = await message.channel.send(
                                                "💾 提出形式はどちらにしますか？\n"
                                                + "ファイル形式の場合は `file`、プレーンテキスト形式の場合は `plain` と返信してください。",
                                                reference=msg_done_target,
                                            )
                                            try:
                                                m_item_format = await client.wait_for(
                                                    "message", check=check, timeout=60
                                                )
                                            except asyncio.TimeoutError:
                                                await message.channel.send(
                                                    "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。",
                                                    reference=msg_ask_format,
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

                                                    msg_done_format = (
                                                        await message.channel.send(
                                                            "✅ 提出形式を **"
                                                            + format_fmt
                                                            + "** にしました。",
                                                            reference=m_item_format,
                                                        )
                                                    )

                                                    item_handler = (
                                                        database.getUserParentRole(
                                                            message
                                                        )
                                                    )

                                                    # データベースにコミット
                                                    result = database.addItem(
                                                        item_name,
                                                        item_limit,
                                                        item_target,
                                                        item_handler,
                                                        item_format,
                                                    )

                                                    # リマインダーを作成する
                                                    ## 1日前
                                                    if (
                                                        database.getItemLimit(result)
                                                        - datetime.timedelta(days=1)
                                                        > datetime.datetime.now()
                                                    ):
                                                        reminder_datetime = (
                                                            database.getItemLimit(
                                                                result
                                                            )
                                                            - datetime.timedelta(days=1)
                                                        )
                                                        database.addReminder(
                                                            result,
                                                            database.getItemTarget(
                                                                result
                                                            ),
                                                            reminder_datetime,
                                                        )
                                                    ## 12時間前
                                                    if (
                                                        database.getItemLimit(result)
                                                        - datetime.timedelta(hours=12)
                                                        > datetime.datetime.now()
                                                    ):
                                                        reminder_datetime = (
                                                            database.getItemLimit(
                                                                result
                                                            )
                                                            - datetime.timedelta(
                                                                hours=12
                                                            )
                                                        )
                                                        database.addReminder(
                                                            result,
                                                            database.getItemTarget(
                                                                result
                                                            ),
                                                            reminder_datetime,
                                                        )
                                                    ## 9時間前
                                                    if (
                                                        database.getItemLimit(result)
                                                        - datetime.timedelta(hours=9)
                                                        > datetime.datetime.now()
                                                    ):
                                                        reminder_datetime = (
                                                            database.getItemLimit(
                                                                result
                                                            )
                                                            - datetime.timedelta(
                                                                hours=9
                                                            )
                                                        )
                                                        database.addReminder(
                                                            result,
                                                            database.getItemTarget(
                                                                result
                                                            ),
                                                            reminder_datetime,
                                                        )
                                                    ## 6時間前
                                                    if (
                                                        database.getItemLimit(result)
                                                        - datetime.timedelta(hours=6)
                                                        > datetime.datetime.now()
                                                    ):
                                                        reminder_datetime = (
                                                            database.getItemLimit(
                                                                result
                                                            )
                                                            - datetime.timedelta(
                                                                hours=6
                                                            )
                                                        )
                                                        database.addReminder(
                                                            result,
                                                            database.getItemTarget(
                                                                result
                                                            ),
                                                            reminder_datetime,
                                                        )
                                                    ## 3時間前
                                                    if (
                                                        database.getItemLimit(result)
                                                        - datetime.timedelta(hours=3)
                                                        > datetime.datetime.now()
                                                    ):
                                                        reminder_datetime = (
                                                            database.getItemLimit(
                                                                result
                                                            )
                                                            - datetime.timedelta(
                                                                hours=3
                                                            )
                                                        )
                                                        database.addReminder(
                                                            result,
                                                            database.getItemTarget(
                                                                result
                                                            ),
                                                            reminder_datetime,
                                                        )
                                                    ## 1時間前
                                                    if (
                                                        database.getItemLimit(result)
                                                        - datetime.timedelta(hours=1)
                                                        > datetime.datetime.now()
                                                    ):
                                                        reminder_datetime = (
                                                            database.getItemLimit(
                                                                result
                                                            )
                                                            - datetime.timedelta(
                                                                hours=1
                                                            )
                                                        )
                                                        database.addReminder(
                                                            result,
                                                            database.getItemTarget(
                                                                result
                                                            ),
                                                            reminder_datetime,
                                                        )

                                                    await message.channel.send(
                                                        "✅ 以下の提出先を登録しました: "
                                                        + "\n📛 項目名: "
                                                        + database.getItemName(result)
                                                        + "\n⏰ 期限: "
                                                        + utils.dtToStr(
                                                            database.getItemLimit(
                                                                result
                                                            )
                                                        )
                                                        + "\n👤 対象: "
                                                        + utils.roleIdToName(
                                                            database.getItemTarget(
                                                                result
                                                            ),
                                                            message.guild,
                                                        )
                                                        + "\n💾 種類: "
                                                        + format_fmt
                                                        + "\n"
                                                        + "\n今までに登録した項目は、`!item list` で参照してください。",
                                                        reference=msg_done_format,
                                                    )
                                                else:
                                                    await message.channel.send(
                                                        "⚠ 提出形式が正確に指定されていません。\n"
                                                        + "`file` か `plain` のどちらかを返信してください。\n"
                                                        + "もう一度、最初から操作をやり直してください。",
                                                        reference=m_item_format,
                                                    )

                                    else:
                                        await message.channel.send(
                                            "⚠ 対象者が正確に指定されていません。\n"
                                            + "__Discord のメンション機能を使用して、__ロールを指定してください。\n"
                                            + "もう一度、最初から操作をやり直してください。",
                                            reference=m_item_target,
                                        )

                        else:
                            await message.channel.send(
                                "⚠ 指定された期限をうまく解釈できませんでした。\n"
                                + "入力例: 2022年4月1日 21時30分 としたい場合は、`2022/4/1 21:30` と入力します。\n"
                                + "もう一度、最初から操作をやり直してください。",
                                reference=m_item_limit,
                            )
        else:
            await message.channel.send("⚠ このコマンドを実行する権限がありません。", reference=message)


# 提出先の登録
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
                if database.getItemLimit(response[0]) < datetime.datetime.now():
                    await message.channel.send("⚠ 提出期限が過ぎています。この提出先に提出することはできません。")
                # 種類が file または plain で指定されていることを確認する。
                elif response[3] == "file" or response[3] == "plain":
                    result = database.addItem(response[0], dt, role_id, response[3])
                    # 種類を日本語に変換し、可読性を良くする
                    format_fmt = ""
                    if response[3] == "file":
                        format_fmt = "📄 ファイル"
                    else:
                        format_fmt = "📜 プレーンテキスト"

                    # リマインダーを作成する
                    ## 1日前
                    reminder_datetime = database.getItemLimit(
                        result
                    ) - datetime.timedelta(days=1)
                    database.addReminder(
                        result, database.getItemTarget(result), reminder_datetime
                    )
                    ## 12時間前
                    reminder_datetime = database.getItemLimit(
                        result
                    ) - datetime.timedelta(hours=12)
                    database.addReminder(
                        result, database.getItemTarget(result), reminder_datetime
                    )
                    ## 9時間前
                    reminder_datetime = database.getItemLimit(
                        result
                    ) - datetime.timedelta(hours=9)
                    database.addReminder(
                        result, database.getItemTarget(result), reminder_datetime
                    )
                    ## 6時間前
                    reminder_datetime = database.getItemLimit(
                        result
                    ) - datetime.timedelta(hours=6)
                    database.addReminder(
                        result, database.getItemTarget(result), reminder_datetime
                    )
                    ## 3時間前
                    reminder_datetime = database.getItemLimit(
                        result
                    ) - datetime.timedelta(hours=3)
                    database.addReminder(
                        result, database.getItemTarget(result), reminder_datetime
                    )
                    ## 1時間前
                    reminder_datetime = database.getItemLimit(
                        result
                    ) - datetime.timedelta(hours=1)
                    database.addReminder(
                        result, database.getItemTarget(result), reminder_datetime
                    )

                    await message.channel.send(
                        "✅ 以下の提出先を登録しました: "
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
            + "[名前]: 項目名を指定してください。\n"
            + "[期限]: 提出期限を `西暦-月-日-時-分` で指定してください。(例: `2022-04-19-18-00`)\n"
            + "[対象]: その提出先に提出するべきロールをメンションしてください。(例: `@サークルA`)\n"
            + "[種類]: 提出の形式を、ファイルの場合は `file`、テキストの場合は `plain` で指定します。"
        )


# 登録された提出先の削除
async def delItem(message):
    response = parse("!item delete {}", message.content)
    if response:
        item_name = database.getItemName(response[0])
        result = database.delItem(response[0])
        if result is False:
            await message.channel.send("⚠ 提出先が見つかりません。ID をご確認ください。")
        else:
            # リマインダーを削除
            reminders = database.getReminder(item_id=int(response[0]))

            for reminder in reminders:
                database.delReminder(reminder.id)
            await message.channel.send("✅ 提出先 " + item_name + " を削除しました。")
    else:
        await message.channel.send("❌ コマンドが不正です。")


# 登録された提出先の削除 (対話方式)
async def delItemInteract(client, message):
    result = database.getRole(message.channel.id)

    if result is None:
        msg_ask_role = await message.channel.send(
            ":mage: どのロールの提出先を削除しますか？\n__Discord のメンション機能を使用して、__ロールを指定してください。"
        )

        def check(m):
            return m.channel == message.channel and m.author == message.author

        try:
            msg = await client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await message.channel.send(
                "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", reference=msg_ask_role
            )
        else:
            target_id = utils.mentionToRoleId(msg.content)

            if target_id is None:
                await message.channel.send(
                    "⚠ ロールの指定方法が間違っています。Discord のメンション機能を用いて、ロールを指定してください。",
                    reference=msg,
                )
            else:
                target = message.guild.get_role(int(target_id))

                if target is None:
                    await message.channel.send(
                        "⚠ 対象のロールが見つかりませんでした。指定しているロールが本当に正しいか、再確認してください。",
                        reference=msg,
                    )
                else:
                    if (
                        database.getTc(target.id, "post") is None
                        and database.isParentRole(target.id) is False
                    ):
                        await message.channel.send(
                            "⚠ ロール **"
                            + target.name
                            + "** は、提出を指示する先のロールとしては登録されていません。",
                            reference=msg,
                        )
                    else:
                        msg_ask_item = await message.channel.send(
                            "**"
                            + utils.roleIdToName(target.id, message.guild)
                            + "** に提出が指示された提出先は以下の通りです: \n"
                            + returnItemByRoleId(target.id, "all")
                            + "\nどの提出先を削除しますか？",
                            reference=msg,
                        )
                        try:
                            msg_item_id = await client.wait_for(
                                "message", check=check, timeout=60
                            )
                        except asyncio.TimeoutError:
                            await message.channel.send(
                                "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。",
                                reference=msg_ask_item,
                            )
                        else:
                            item_id = msg_item_id.content
                            if item_id.isdigit():
                                item_name = database.getItemName(item_id)
                                result = database.delItem(item_id)
                                if result is False:
                                    await message.channel.send(
                                        "⚠ 提出先が見つかりません。ID をご確認ください。",
                                        reference=msg_item_id,
                                    )
                                else:
                                    # リマインダーを削除
                                    reminders = database.getReminder(
                                        item_id=int(item_id)
                                    )

                                    for reminder in reminders:
                                        database.delReminder(reminder.id)

                                    await message.channel.send(
                                        "✅ 提出先 " + item_name + " を削除しました。",
                                        reference=msg_item_id,
                                    )
                            else:
                                await message.channel.send(
                                    "⚠ 提出先の指定方法が間違っています。\n" + "もう一度、最初から操作をやり直してください。",
                                    reference=msg_item_id,
                                )
    else:
        await message.channel.send(
            "**"
            + utils.roleIdToName(
                int(database.getRole(message.channel.id)), message.guild
            )
            + "** に提出が指示された提出先は以下の通りです: \n"
            + returnItem(message, "all")
            + "\nどの提出先を削除しますか？"
        )
        try:
            msg_item_id = await client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await message.channel.send("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
        else:
            item_id = msg_item_id.content
            if item_id.isdigit():
                item_name = database.getItemName(item_id)
                result = database.delItem(item_id)
                if result is False:
                    await message.channel.send("⚠ 提出先が見つかりません。ID をご確認ください。")
                else:
                    await message.channel.send("✅ 提出先 " + item_name + " を削除しました。")
            else:
                await message.channel.send(
                    "⚠ 提出先の指定方法が間違っています。\n" + "もう一度、最初から操作をやり直してください。"
                )


# 登録された提出先を表示, 特定のロールに紐付いた提出先のみ表示する
async def listItem(client, message):
    result = database.getRole(message.channel.id)

    if result is None:
        msg_ask_item = await message.channel.send(
            ":mage: どのロールの提出先を確認しますか？\n__Discord のメンション機能を使用して、__ロールを指定してください。"
        )

        def check(m):
            return m.channel == message.channel and m.author == message.author

        try:
            msg = await client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await message.channel.send(
                "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", reference=msg_ask_item
            )
        else:
            target_id = utils.mentionToRoleId(msg.content)

            if target_id is None:
                await message.channel.send(
                    "⚠ ロールの指定方法が間違っています。Discord のメンション機能を用いて、ロールを指定してください。",
                    reference=msg,
                )
            else:
                target = message.guild.get_role(int(target_id))

                if target is None:
                    await message.channel.send(
                        "⚠ 対象のロールが見つかりませんでした。指定しているロールが本当に正しいか、再確認してください。",
                        reference=msg,
                    )
                else:
                    if (
                        database.getTc(target.id, "post") is None
                        and database.isParentRole(target.id) is False
                    ):
                        await message.channel.send(
                            "⚠ ロール **"
                            + target.name
                            + "** は、提出を指示する先のロールとしては登録されていません。",
                            reference=msg,
                        )
                    else:
                        await message.channel.send(
                            "**"
                            + utils.roleIdToName(target.id, message.guild)
                            + "** に提出が指示された提出先は以下の通りです: \n"
                            + returnItemByRoleId(target.id, "all"),
                            reference=msg,
                        )
    else:
        await message.channel.send(
            "**"
            + utils.roleIdToName(
                int(database.getRole(message.channel.id)), message.guild
            )
            + "** に提出が指示された提出先は以下の通りです: \n"
            + returnItem(message, "all"),
            reference=message,
        )


# ファイルを提出する
async def submitFileItem(client, message):
    if not message.author.bot:
        if returnItem(message, "file") == "今のところ、提出を指示されている項目はありません。":
            print(
                "parent role: "
                + str(database.getParentRole(database.getRole(message.channel.id)))
            )
            await message.channel.send(
                "⚠ ファイルを検出しましたが、あなたが提出するべき項目は登録されていません。\n"
                + "委員会が提出先を登録するまで、しばらくお待ちください。",
                reference=message,
            )
        else:
            channel = message.channel

            msg_ask_item = await channel.send(
                "❗ ファイルを検出しました。\n"
                + "何を提出しようとしていますか？\n"
                + returnItem(message, "file")
                + "\n提出したい項目の ID を、このチャンネルで発言してください。",
                reference=message,
            )

            def check(m):
                return m.channel == channel and m.author == message.author

            try:
                msg = await client.wait_for("message", check=check, timeout=60)

            except asyncio.TimeoutError:
                await channel.send(
                    "⚠ タイムアウトしました。もう一度、ファイルのアップロードからやり直してください。", reference=msg_ask_item
                )
            else:
                if database.getItemName(msg.content) is False:
                    await channel.send(
                        "⚠ 指定された ID は間違っています。もう一度、ファイルのアップロードからやり直してください。",
                        reference=msg,
                    )
                elif database.getItemLimit(msg.content) < datetime.datetime.now():
                    await message.channel.send(
                        "⚠ 提出期限が過ぎています。この提出先に提出することはできません。", reference=msg
                    )
                else:
                    target = database.getItemTarget(msg.content)
                    role_id = database.getRole(message.channel.id)
                    parent_role_id = database.getParentRole(
                        database.getRole(message.channel.id)
                    )

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
                                        database.getRole(message.channel.id),
                                        message.guild,
                                    )  # ロール名
                                    + "_"
                                    + database.getItemName(msg.content)
                                    + "_"
                                    + attachment.filename
                                )
                                await attachment.save(path)
                                item_count += 1
                                submit_id = database.addSubmit(
                                    msg.content,  # item_id
                                    dt_now,  # datetime
                                    filename,  # filename
                                    path,  # path, サーバー上のファイルの場所
                                    None,  # plain, file なので NULL
                                    message.author.id,  # author, 提出者の Discord 内部 ID
                                    database.getRole(
                                        message.channel.id
                                    ),  # author_role, 提出者のロール ID
                                    database.getItemTarget(msg.content),  # target
                                    "file",  # format
                                )

                            # リマインダーを削除
                            reminders = database.getReminder(
                                item_id=int(msg.content),
                                target=int(database.getRole(message.channel.id)),
                            )

                            for reminder in reminders:
                                print(str(reminder.id))
                                database.delReminder(reminder.id)

                            await channel.send(
                                "✅ 提出物 "
                                + "**"
                                + database.getItemName(msg.content)
                                + "** を提出しました。("
                                + str(item_count)
                                + "件のファイル)",
                                reference=msg,
                            )
                            await sendNotify(submit_id, client, message.guild)
                        elif database.getItemFormat(msg.content) == "plain":
                            await channel.send(
                                "⚠ 提出物 "
                                + "**"
                                + database.getItemName(msg.content)
                                + "** はファイルではなくテキストで提出してください。",
                                reference=msg,
                            )
                        else:
                            await channel.send("⚠ 処理中になんらかの問題が発生しました。", reference=msg)
                    else:
                        await channel.send(
                            "⚠ その提出先はあなたに割り当てられていません。もう一度、ファイルのアップロードからやり直してください。",
                            reference=msg,
                        )


# 提出先の一覧を整形して str として返す (テキストチャンネルの ID で絞り込む)
## format:
## all: すべての提出形式の提出先を返す
## file: ファイル形式の提出先を返す
## plain: プレーンテキスト形式の提出先を返す
def returnItem(message, format):
    items = ""
    # 特定ロールのみに指示された提出先
    for item in database.showItem(database.getRole(message.channel.id), format):
        if item.limit > datetime.datetime.now():
            items += "\n"
            items += "🆔 提出先 ID: " + str(item.id) + "\n"
            items += "📛 項目名: " + item.name + "\n"
            items += "⏰ 提出期限: `" + utils.dtToStr(item.limit) + "`\n"
            if item.format == "file":
                items += "💾 提出形式: 📄 ファイル\n"
            elif item.format == "plain":
                items += "💾 提出形式: 📜 プレーンテキスト\n"
            else:
                items += "💾 提出形式: 不明。委員会までお問い合わせください。\n"
    # 親ロールに指示された提出先
    for item in database.showItem(
        database.getParentRole(database.getRole(message.channel.id)), format
    ):
        if item.limit > datetime.datetime.now():
            items += "\n"
            items += "🆔 提出先 ID: " + str(item.id) + "\n"
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


# 提出先の一覧を整形して str として返す (Discord 上のロール ID で絞り込む)
## format:
## all: すべての提出形式の提出先を返す
## file: ファイル形式の提出先を返す
## plain: プレーンテキスト形式の提出先を返す
def returnItemByRoleId(role_id, format):
    items = ""
    for item in database.showItem(role_id, format):
        if item.limit > datetime.datetime.now():
            items += "\n"
            items += "🆔 提出先 ID: " + str(item.id) + "\n"
            items += "📛 項目名: " + item.name + "\n"
            items += "⏰ 提出期限: `" + utils.dtToStr(item.limit) + "`\n"
            if item.format == "file":
                items += "💾 提出形式: 📄 ファイル\n"
            elif item.format == "plain":
                items += "💾 提出形式: 📜 プレーンテキスト\n"
            else:
                items += "💾 提出形式: 不明。委員会までお問い合わせください。\n"
    if not database.isParentRole(role_id):
        for item in database.showItem(database.getParentRole(role_id), format):
            if item.limit > datetime.datetime.now():
                items += "\n"
                items += "🆔 提出先 ID: " + str(item.id) + "\n"
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
        msg_ask_role = await message.channel.send(
            ":man_mage: どのロールに指示された提出物の履歴を確認しますか？\n"
            + "Discord のメンション機能を用いて、ロールを指定してください。",
            reference=message,
        )

        try:
            msg_role = await client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await message.channel.send(
                "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", reference=msg_ask_role
            )
        else:
            target_id = utils.mentionToRoleId(msg_role.content)

            if target_id is None:
                await message.channel.send(
                    "⚠ ロールの指定方法が間違っています。Discord のメンション機能を用いて、ロールを指定してください。",
                    reference=msg_role,
                )
            else:
                target = message.guild.get_role(int(target_id))

                if target is None:
                    await message.channel.send(
                        "⚠ 対象のロールが見つかりませんでした。指定しているロールが本当に正しいか、再確認してください。",
                        reference=msg_role,
                    )
                else:
                    if (
                        database.getTc(target.id, "post") is None
                        and database.isParentRole(target.id) is False
                    ):
                        await message.channel.send(
                            "⚠ ロール **"
                            + target.name
                            + "** は、提出を指示する先のロールとしては登録されていません。",
                            reference=msg_role,
                        )
                    else:
                        if (
                            returnItemByRoleId(target.id, "all")
                            == "今のところ、提出を指示されている項目はありません。"
                        ):
                            await message.channel.send(
                                ":person_bowing: ロール **"
                                + target.name
                                + "** に指示されている提出物は、今のところありません。",
                                reference=msg_role,
                            )
                        else:
                            msg_ask_item = await message.channel.send(
                                "**"
                                + utils.roleIdToName(target.id, message.guild)
                                + "** に提出が指示された提出物は以下の通りです。\n"
                                + "履歴を閲覧したい項目を選んでください。"
                                + returnItemByRoleId(target.id, "all"),
                                reference=msg_role,
                            )
                            try:
                                msg_item_id = await client.wait_for(
                                    "message", check=check, timeout=60
                                )
                            except asyncio.TimeoutError:
                                await message.channel.send(
                                    "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。",
                                    reference=msg_ask_item,
                                )
                            else:
                                if msg_item_id.content.isdigit():
                                    if (
                                        database.getItemLimit(msg_item_id.content)
                                        is None
                                    ):
                                        await message.channel.send(
                                            "⚠ 指定された ID **"
                                            + msg_item_id.content
                                            + "** を持つ提出先が見つかりませんでした。",
                                            reference=msg_item_id,
                                        )
                                    else:
                                        item_id = msg_item_id.content

                                        submit_list = database.getSubmitList(
                                            item_id, None
                                        )
                                        list_fmt = formatSubmitList(
                                            client, submit_list, "all"
                                        )

                                        await message.channel.send(
                                            ":information_source: 以下が提出先 **"
                                            + database.getItemName(item_id)
                                            + "** (対象: "
                                            + utils.roleIdToName(
                                                database.getItemTarget(item_id),
                                                message.guild,
                                            )
                                            + ", "
                                            + "提出者: "
                                            + utils.roleIdToName(
                                                database.getSubmitAuthorRole(item_id),
                                                message.guild,
                                            )
                                            + ") の提出履歴です。\n"
                                            + list_fmt,
                                            reference=msg_item_id,
                                        )
                                else:
                                    await message.channel.send(
                                        "⚠ 番号で提出先 ID を指定してください。もう一度、最初から操作をやり直してください。",
                                        reference=msg_item_id,
                                    )
    else:
        if returnItem(message, "all") == "今のところ、提出を指示されている項目はありません。":
            await message.channel.send(
                ":person_bowing: ロール **"
                + utils.roleIdToName(
                    int(database.getRole(message.channel.id)), message.guild
                )
                + "** に指示されている提出物は、今のところありません。",
                reference=message,
            )
        else:
            msg_ask_item = await message.channel.send(
                "**"
                + utils.roleIdToName(
                    int(database.getRole(message.channel.id)), message.guild
                )
                + "** に提出が指示されたものは以下の通りです。 \n"
                + "履歴を閲覧したい項目を選んでください: \n"
                + returnItem(message, "all"),
                reference=message,
            )
            try:
                msg_item_id = await client.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                await message.channel.send(
                    "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", reference=msg_ask_item
                )
            else:
                if msg_item_id.content.isdigit():
                    if database.getItemLimit(msg_item_id.content) is None:
                        await message.channel.send(
                            "⚠ 指定された ID **"
                            + msg_item_id.content
                            + "** を持つ提出先が見つかりませんでした。",
                            reference=msg_item_id,
                        )
                    else:
                        item_id = message.content = unicodedata.normalize(
                            "NFKC", msg_item_id.content
                        )

                        submit_list = database.getSubmitList(
                            item_id, database.getRole(message.channel.id)
                        )
                        list_fmt = formatSubmitList(client, submit_list, "all")

                        await message.channel.send(
                            ":information_source: 以下が提出先 **"
                            + database.getItemName(item_id)
                            + "** (対象: "
                            + utils.roleIdToName(
                                database.getItemTarget(item_id), message.guild
                            )
                            + ", 提出元: "
                            + utils.roleIdToName(
                                database.getRole(message.channel.id), message.guild
                            )
                            + ") の提出履歴です。\n"
                            + list_fmt,
                            reference=msg_item_id,
                        )
                else:
                    await message.channel.send(
                        "⚠ 番号で提出先 ID を指定してください。もう一度、最初から操作をやり直してください。"
                    )


async def getSubmitInteract(client, message):
    result = database.getRole(message.channel.id)

    def check(m):
        return m.channel == message.channel and m.author == message.author

    if result is None:
        msg_ask_item = await message.channel.send(
            ":man_mage: どのロールが提出した提出物をダウンロードしますか？\n"
            + "Discord のメンション機能を用いて、ロールを指定してください。"
        )

        try:
            msg_role = await client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await message.channel.send(
                "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", reference=msg_ask_item
            )
        else:
            target_id = utils.mentionToRoleId(msg_role.content)

            if target_id is None:
                await message.channel.send(
                    "⚠ ロールの指定方法が間違っています。Discord のメンション機能を用いて、ロールを指定してください。",
                    reference=msg_role,
                )
            else:
                target = message.guild.get_role(int(target_id))

                if target is None:
                    await message.channel.send(
                        "⚠ 対象のロールが見つかりませんでした。指定しているロールが本当に正しいか、再確認してください。",
                        reference=msg_role,
                    )
                else:
                    if (
                        database.getTc(target.id, "post") is None
                        and database.isParentRole(target.id) is False
                    ):
                        await message.channel.send(
                            "⚠ ロール **"
                            + target.name
                            + "** は、提出を指示する先のロールとしては登録されていません。",
                            reference=msg_role,
                        )
                    else:
                        if (
                            returnItemByRoleId(target.id, "all")
                            == "今のところ、提出を指示されている項目はありません。"
                        ):
                            await message.channel.send(
                                ":person_bowing: ロール **"
                                + target.name
                                + "** に指示されている提出物は、今のところありません。",
                                reference=msg_role,
                            )
                        else:
                            msg_ask_item = await message.channel.send(
                                "**"
                                + utils.roleIdToName(target.id, message.guild)
                                + "** に提出が指示された提出物は以下の通りです。\n"
                                + "ダウンロードしたい項目を選んでください。"
                                + returnItemByRoleId(target.id, "all"),
                                reference=msg_role,
                            )
                            try:
                                msg_item_id = await client.wait_for(
                                    "message", check=check, timeout=60
                                )
                            except asyncio.TimeoutError:
                                await message.channel.send(
                                    "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。",
                                    reference=msg_ask_item,
                                )
                            else:
                                item_id = message.content = unicodedata.normalize(
                                    "NFKC", msg_item_id.content
                                )
                                if item_id.isdigit():
                                    if database.getItemLimit(item_id) is None:
                                        await message.channel.send(
                                            "⚠ 指定された ID **"
                                            + msg_item_id.content
                                            + "** を持つ提出先が見つかりませんでした。",
                                            reference=msg_item_id,
                                        )
                                    else:
                                        # ファイルの場合
                                        if database.getItemFormat(item_id) == "file":
                                            submit_list = database.getSubmitList(
                                                item_id, None
                                            )
                                            list_fmt = formatSubmitList(
                                                client, submit_list, "file"
                                            )

                                            msg_ask_file = await message.channel.send(
                                                ":information_source: 以下が提出先 **"
                                                + database.getItemName(item_id)
                                                + "** (対象: "
                                                + utils.roleIdToName(
                                                    database.getItemTarget(item_id),
                                                    message.guild,
                                                )
                                                + ") の提出履歴です。\n"
                                                + "ダウンロードしたいファイルを選んでください。\n"
                                                + list_fmt,
                                                reference=msg_item_id,
                                            )

                                            try:
                                                msg_submit_id = await client.wait_for(
                                                    "message", check=check, timeout=60
                                                )
                                            except asyncio.TimeoutError:
                                                await message.channel.send(
                                                    "⚠ タイムアウトしました。"
                                                    + "もう一度、最初から操作をやり直してください。",
                                                    reference=msg_ask_file,
                                                )
                                            else:
                                                submit_id = unicodedata.normalize(
                                                    "NFKC", msg_submit_id.content
                                                )
                                                if (
                                                    database.getSubmitAuthor(submit_id)
                                                    is None
                                                ):
                                                    await message.channel.send(
                                                        "⚠ 提出 ID が間違っています。"
                                                        + "もう一度、最初から操作をやり直してください。",
                                                        reference=msg_submit_id,
                                                    )
                                                else:
                                                    await message.channel.send(
                                                        "✅ 以下の提出を送信します: \n\n"
                                                        + formatSubmit(
                                                            client,
                                                            database.getSubmit(
                                                                submit_id
                                                            ),
                                                        ),
                                                        file=discord.File(
                                                            database.getSubmit(
                                                                submit_id
                                                            ).path,
                                                            filename=utils.convFileName(
                                                                database.getSubmit(
                                                                    submit_id
                                                                ).path
                                                            ),
                                                        ),
                                                        reference=msg_submit_id,
                                                    )
                                        elif database.getItemFormat(item_id) == "plain":
                                            tmp_dir = "./data/tmp"
                                            if not os.path.exists(tmp_dir):
                                                os.makedirs(tmp_dir)
                                            submit_list = database.getSubmitList(
                                                item_id, None
                                            )
                                            JST = dateutil.tz.gettz("Asia/Tokyo")
                                            dt_now = datetime.datetime.now(JST)
                                            fmt_dt = utils.dtToStrFileName(dt_now)
                                            # ファイル名の例: 2022-05-02_16-15_提出先A.csv
                                            filename = (
                                                fmt_dt
                                                + "_"
                                                + database.getItemName(item_id)
                                                + ".xlsx"
                                            )
                                            save_path = tmp_dir + "/" + filename

                                            # 各列のために用意する配列
                                            export_list = []
                                            submit_id_list = []
                                            submit_datetime_list = []
                                            submit_author_list = []
                                            submit_author_role_list = []
                                            submit_plain_list = []
                                            submit_verified_list = []

                                            for submit in submit_list:
                                                submit_id_list.append(submit.id)
                                                submit_datetime_list.append(
                                                    utils.dtToStr(submit.datetime)
                                                )
                                                submit_author_list.append(
                                                    utils.userIdToName(
                                                        client, submit.author
                                                    )
                                                )
                                                submit_author_role_list.append(
                                                    utils.roleIdToName(
                                                        submit.author_role,
                                                        message.guild,
                                                    )
                                                )
                                                if submit.plain is None:
                                                    submit_plain_list.append("未記入")
                                                else:
                                                    submit_plain_list.append(
                                                        submit.plain
                                                    )
                                                if submit.verified:
                                                    submit_verified_list.append("済")
                                                else:
                                                    submit_verified_list.append("未")

                                            export_list.append(submit_id_list)
                                            export_list.append(submit_datetime_list)
                                            export_list.append(submit_author_list)
                                            export_list.append(submit_author_role_list)
                                            export_list.append(submit_plain_list)
                                            export_list.append(submit_verified_list)

                                            df = pd.DataFrame(export_list)
                                            df.index = [
                                                "提出 ID",
                                                "提出日時",
                                                "提出者",
                                                "提出元ロール",
                                                "提出内容",
                                                "承認",
                                            ]

                                            df.T.to_excel(
                                                save_path,
                                                sheet_name=database.getItemName(
                                                    item_id
                                                ),
                                            )

                                            await message.channel.send(
                                                ":mage: 提出先 **"
                                                + database.getItemName(item_id)
                                                + "** (対象: "
                                                + utils.roleIdToName(
                                                    database.getItemTarget(item_id),
                                                    message.guild,
                                                )
                                                + ") に提出された内容を Excel (`.xlsx`) ファイルとして送信します。",
                                                file=discord.File(
                                                    save_path,
                                                    filename=utils.convFileName(
                                                        filename
                                                    ),
                                                ),
                                                reference=msg_item_id,
                                            )
                                        else:
                                            await message.channel.send(
                                                "⚠ 処理中に問題が発生しました。もう一度、最初から操作をやり直してください。"
                                            )

                                else:
                                    await message.channel.send(
                                        "⚠ 番号で提出先 ID を指定してください。もう一度、最初から操作をやり直してください。",
                                        reference=msg_item_id,
                                    )
    else:
        if returnItem(message, "all") == "今のところ、提出を指示されている項目はありません。":
            await message.channel.send(
                ":person_bowing: ロール **"
                + utils.roleIdToName(
                    int(database.getRole(message.channel.id)), message.guild
                )
                + "** に指示されている提出物は、今のところありません。\n"
                + "したがって、何もダウンロードできるものはありません。",
                reference=message,
            )
        else:
            msg_ask_item = await message.channel.send(
                "**"
                + utils.roleIdToName(
                    int(database.getRole(message.channel.id)), message.guild
                )
                + "** に提出が指示されたものは以下の通りです。 \n"
                + "ダウンロードしたい項目を選んでください: \n"
                + returnItem(message, "all"),
                reference=message,
            )
            try:
                msg_item_id = await client.wait_for("message", check=check, timeout=60)
            except asyncio.TimeoutError:
                await message.channel.send(
                    "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", reference=msg_ask_item
                )
            else:
                item_id = unicodedata.normalize("NFKC", msg_item_id.content)
                if item_id.isdigit():
                    if database.getItemLimit(item_id) is None:
                        await message.channel.send(
                            "⚠ 指定された ID **" + item_id + "** を持つ提出先が見つかりませんでした。",
                            reference=msg_item_id,
                        )
                    else:
                        submit_list = database.getSubmitList(
                            item_id, database.getRole(message.channel.id)
                        )
                        # ファイルの場合
                        if database.getItemFormat(item_id) == "file":
                            list_fmt = formatSubmitList(client, submit_list, "file")

                            msg_ask_file = await message.channel.send(
                                ":information_source: 以下が提出先 **"
                                + database.getItemName(item_id)
                                + "** (対象: "
                                + utils.roleIdToName(
                                    database.getItemTarget(item_id), message.guild
                                )
                                + ", 提出元: "
                                + utils.roleIdToName(
                                    database.getRole(message.channel.id), message.guild
                                )
                                + ") の提出履歴です。\n"
                                + "ダウンロードしたいファイルを選んでください。\n\n"
                                + list_fmt,
                                reference=msg_item_id,
                            )
                            try:
                                msg_submit_id = await client.wait_for(
                                    "message", check=check, timeout=60
                                )
                            except asyncio.TimeoutError:
                                await message.channel.send(
                                    "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。",
                                    reference=msg_ask_file,
                                )
                            else:
                                submit_id = unicodedata.normalize(
                                    "NFKC", msg_submit_id.content
                                )
                                if database.getSubmitAuthor(submit_id) is None:
                                    await message.channel.send(
                                        "⚠ 提出 ID が間違っています。もう一度、最初から操作をやり直してください。",
                                        reference=msg_submit_id,
                                    )
                                else:
                                    await message.channel.send(
                                        "✅ 以下の提出を送信します: \n\n"
                                        + formatSubmit(
                                            client, database.getSubmit(submit_id)
                                        ),
                                        file=discord.File(
                                            database.getSubmit(submit_id).path,
                                            filename=utils.convFileName(
                                                database.getSubmit(submit_id).path
                                            ),
                                            spoiler=False,
                                        ),
                                        reference=msg_submit_id,
                                    )
                        elif database.getItemFormat(item_id) == "plain":
                            tmp_dir = "./data/tmp"
                            if not os.path.exists(tmp_dir):
                                os.makedirs(tmp_dir)
                            JST = dateutil.tz.gettz("Asia/Tokyo")
                            dt_now = datetime.datetime.now(JST)
                            fmt_dt = utils.dtToStrFileName(dt_now)
                            # ファイル名の例: 2022-05-02_16-15_提出先A.csv
                            filename = (
                                fmt_dt + "_" + database.getItemName(item_id) + ".xlsx"
                            )
                            save_path = tmp_dir + "/" + filename

                            # 各列のために用意する配列
                            export_list = []
                            submit_id_list = []
                            submit_datetime_list = []
                            submit_author_list = []
                            submit_author_role_list = []
                            submit_plain_list = []
                            submit_verified_list = []

                            for submit in submit_list:
                                submit_id_list.append(submit.id)
                                submit_datetime_list.append(
                                    utils.dtToStr(submit.datetime)
                                )
                                submit_author_list.append(
                                    utils.userIdToName(client, submit.author)
                                )
                                submit_author_role_list.append(
                                    utils.roleIdToName(
                                        submit.author_role, message.guild
                                    )
                                )
                                if submit.plain is None:
                                    submit_plain_list.append("未記入")
                                else:
                                    submit_plain_list.append(submit.plain)
                                if submit.verified:
                                    submit_verified_list.append("済")
                                else:
                                    submit_verified_list.append("未")

                            export_list.append(submit_id_list)
                            export_list.append(submit_datetime_list)
                            export_list.append(submit_author_list)
                            export_list.append(submit_author_role_list)
                            export_list.append(submit_plain_list)
                            export_list.append(submit_verified_list)

                            df = pd.DataFrame(export_list)
                            df.index = ["提出 ID", "提出日時", "提出者", "提出元ロール", "提出内容", "承認"]

                            df.T.to_excel(
                                save_path, sheet_name=database.getItemName(item_id)
                            )

                            await message.channel.send(
                                ":mage: 提出先 **"
                                + database.getItemName(item_id)
                                + "** (対象: "
                                + utils.roleIdToName(
                                    database.getItemTarget(item_id), message.guild
                                )
                                + ") に提出された内容を Excel (`.xlsx`) ファイルとして送信します。",
                                file=discord.File(
                                    save_path,
                                    filename=utils.convFileName(filename),
                                ),
                                reference=msg_item_id,
                            )
                        else:
                            await message.channel.send(
                                "⚠ 処理中に問題が発生しました。もう一度、最初から操作をやり直してください。"
                            )
                else:
                    await message.channel.send(
                        "⚠ 番号で提出先 ID を指定してください。もう一度、最初から操作をやり直してください。",
                        reference=msg_item_id,
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


async def verifySubmitInteract(client, message):
    msg_ask_role = await message.channel.send(
        "📛 どのロールに指示された提出物を承認しますか？\n" + "Discord のメンション機能を使用して、ロールを指定してください。",
        reference=message,
    )

    def check(m):
        return m.channel == message.channel and m.author == message.author

    try:
        m_role_name = await client.wait_for("message", check=check, timeout=60)
    except asyncio.TimeoutError:
        await message.channel.send(
            "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", reference=msg_ask_role
        )
    else:
        if utils.mentionToRoleId(m_role_name.content) is None:
            await message.channel.send(
                "⚠ ロールの指定方法が間違っています。Discord のメンション機能を用いてロールを指定してください。\n"
                + "もう一度、最初から操作をやり直してください。",
                reference=m_role_name,
            )
        else:
            target = message.guild.get_role(
                int(utils.mentionToRoleId(m_role_name.content))
            )
            if target is None:
                await message.channel.send(
                    "⚠ 対象のロールが見つかりませんでした。指定しているロールが本当に正しいか、再確認してください。\n"
                    + "もう一度、最初から操作をやり直してください。",
                    reference=m_role_name,
                )
            else:
                if (
                    database.getTc(target.id, "post") is None
                    and database.isParentRole(target.id) is False
                ):
                    await message.channel.send(
                        "⚠ ロール **" + target.name + "** は、提出を指示する先のロールとしては登録されていません。",
                        reference=m_role_name,
                    )
                else:
                    msg_ask_item = await message.channel.send(
                        "**"
                        + utils.roleIdToName(target.id, message.guild)
                        + "** に提出が指示された提出物は以下の通りです: \n"
                        + returnItemByRoleId(target.id, "all")
                        + "\n目的の提出先 ID を返信してください。",
                        reference=m_role_name,
                    )

                    def check(m):
                        return (
                            m.channel == message.channel and m.author == message.author
                        )

                    try:
                        m_item_id = await client.wait_for(
                            "message", check=check, timeout=60
                        )
                    except asyncio.TimeoutError:
                        await message.channel.send(
                            "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。",
                            reference=msg_ask_item,
                        )
                    else:
                        item_id = m_item_id.content

                        submit_list = database.getSubmitList(item_id, None)
                        list_fmt = formatSubmitList(client, submit_list, "all")

                        await message.channel.send(
                            ":information_source: 以下が提出先 **"
                            + database.getItemName(item_id)
                            + "** (対象: "
                            + utils.roleIdToName(
                                database.getItemTarget(item_id),
                                message.guild,
                            )
                            + ", "
                            + "提出者: "
                            + utils.roleIdToName(
                                database.getSubmitAuthorRole(item_id),
                                message.guild,
                            )
                            + ") の提出履歴です。\n"
                            + list_fmt,
                            reference=m_item_id,
                        )
                        if list_fmt == "まだ、この項目に対して何も提出されていません。":
                            pass
                        else:
                            msg_ask_submit = await message.channel.send(
                                "承認したい提出の ID を返信してください。", reference=m_item_id
                            )
                            try:
                                m_submit_id = await client.wait_for(
                                    "message", check=check, timeout=60
                                )
                            except asyncio.TimeoutError:
                                await message.channel.send(
                                    "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。",
                                    reference=msg_ask_submit,
                                )
                            else:
                                submit_id = unicodedata.normalize(
                                    "NFKC", m_submit_id.content
                                )
                                if submit_id.isdigit():
                                    result = database.verifySubmit(submit_id)
                                    if result is None:
                                        await message.channel.send(
                                            "⚠ 指定した提出は存在しません。\n"
                                            + "もう一度、最初から操作をやり直してください。",
                                            reference=m_submit_id,
                                        )
                                    else:
                                        submit = database.getSubmit(submit_id)
                                        await message.channel.send(
                                            "✅ 提出 ID: "
                                            + submit_id
                                            + " (提出先: "
                                            + database.getItemName(submit.item_id)
                                            + ", "
                                            + "対象: "
                                            + utils.roleIdToName(
                                                database.getItemTarget(submit.item_id),
                                                message.guild,
                                            )
                                            + ") を承認しました。",
                                            reference=m_submit_id,
                                        )
                                else:
                                    await message.channel.send(
                                        "⚠ 提出 ID の指定方法が間違っています。\n"
                                        + "もう一度、最初から操作をやり直してください。",
                                        reference=m_submit_id,
                                    )


# submitPlainText(client, message): プレーンテキスト方式の提出先に提出する (対話方式)
async def submitPlainTextInteract(client, message):
    if returnItem(message, "plain") == "今のところ、提出を指示されている項目はありません。":
        await message.channel.send(
            "⚠ あなたが提出するべき項目は登録されていません。\n" + "委員会が提出先を登録するまで、しばらくお待ちください。",
            reference=message,
        )
    else:
        msg_ask_item = await message.channel.send(
            ":mage: どの提出先に提出しようとしていますか？\n"
            + returnItem(message, "plain")
            + "\n提出したい項目の ID を、このチャンネルで発言してください。",
            reference=message,
        )

        def check(m):
            return m.channel == message.channel and m.author == message.author

        try:
            msg = await client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await channel.send(
                "⚠ タイムアウトしました。もう一度、ファイルのアップロードからやり直してください。", reference=msg_ask_item
            )
        else:
            if database.getItemName(msg.content) is False:
                await channel.send(
                    "⚠ 指定された ID は間違っています。もう一度、ファイルのアップロードからやり直してください。", reference=msg
                )
            elif database.getItemLimit(msg.content) < datetime.datetime.now():
                await message.channel.send(
                    "⚠ 提出期限が過ぎています。この提出先に提出することはできません。", reference=msg
                )
            else:
                target = database.getItemTarget(msg.content)
                role_id = database.getRole(message.channel.id)
                parent_role_id = database.getParentRole(
                    database.getRole(message.channel.id)
                )
                # 特定の子ロールだけに指示された提出先
                if target == role_id or target == str(parent_role_id):
                    if database.getItemFormat(msg.content) == "plain":
                        msg_ask_content = await message.channel.send(
                            ":mage: 提出内容はどのようにしますか？\n"
                            + "内容をこのテキストチャンネルに送信してください。\n"
                            + "キャンセルする場合は、このままの状態で30秒放置してください。",
                            reference=msg,
                        )
                        try:
                            msg_submit_content = await client.wait_for(
                                "message", check=check, timeout=60
                            )
                        except asyncio.TimeoutError:
                            await channel.send(
                                "⚠ タイムアウトしました。\n"
                                + "キャンセルを目的としていなかった場合はもう一度、最初から操作をやり直してください。",
                                reference=msg_ask_content,
                            )
                        else:
                            if utils.isValidAsName(msg_submit_content.content):
                                JST = dateutil.tz.gettz("Asia/Tokyo")
                                dt_now = datetime.datetime.now(JST)
                                submit_id = database.addSubmit(
                                    msg.content,  # item_id
                                    dt_now,  # datetime
                                    None,  # filename, plain なので NULL
                                    None,  # path, サーバー上のファイルの場所, plain なので NULL
                                    msg_submit_content.content,  # plain
                                    message.author.id,  # author, 提出者の Discord 内部 ID
                                    database.getRole(
                                        message.channel.id
                                    ),  # author_role, 提出者のロール ID
                                    database.getItemTarget(msg.content),  # target
                                    "plain",  # format
                                )

                                # リマインダーを削除
                                reminders = database.getReminder(
                                    item_id=int(msg.content),
                                    target=database.getRole(message.channel.id),
                                )

                                for reminder in reminders:
                                    database.delReminder(reminder.id)

                                await message.channel.send(
                                    "✅ 提出物 "
                                    + "**"
                                    + database.getItemName(msg.content)
                                    + "** を以下の内容で提出しました:\n"
                                    + "```\n"
                                    + msg_submit_content.content
                                    + "\n"
                                    + "```\n",
                                    reference=msg_submit_content,
                                )

                                await sendNotify(submit_id, client, message.guild)
                            else:
                                message.channel.send(
                                    "⚠ 提出内容として正しくありません。\n" + "もう一度、最初から操作をやり直してください。",
                                    reference=msg_submit_content,
                                )

                    elif database.getItemFormat(msg.content) == "file":
                        await message.channel.send(
                            "⚠ 提出物 "
                            + "**"
                            + database.getItemName(msg.content)
                            + "** はファイルで提出してください。",
                            reference=msg,
                        )
                    else:
                        await message.channel.send("⚠ 処理中になんらかの問題が発生しました。")
                else:
                    await message.channel.send(
                        "⚠ その提出先はあなたに割り当てられていません。" + "もう一度、最初から操作をやり直してください。",
                        reference=msg,
                    )


# checkSubmitInteract(client, message): 各ロールの提出状況を表示する (対話方式)
async def checkSubmitInteract(client, message):
    msg_ask_role = await message.channel.send(
        ":mage: どのロールに指示された提出物の提出状況を確認しますか？\n" + "Discord のメンション機能を使用して、ロールを指定してください。",
        reference=message,
    )

    def check(m):
        return m.channel == message.channel and m.author == message.author

    try:
        m_target = await client.wait_for("message", check=check, timeout=60)
    except asyncio.TimeoutError:
        await message.channel.send(
            "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", reference=msg_ask_role
        )
    else:
        target_id = utils.mentionToRoleId(m_target.content)

        if target_id is None:
            await message.channel.send(
                "⚠ ロールの指定方法が間違っています。Discord のメンション機能を用いて、ロールを指定してください。"
                + "もう一度、最初から操作をやり直してください。",
                reference=m_target,
            )
        else:
            target = message.guild.get_role(int(target_id))

            if target is None:
                await message.channel.send(
                    "⚠ 対象のロールが見つかりませんでした。指定しているロールが本当に正しいか、再確認してください。"
                    + "もう一度、最初から操作をやり直してください。",
                    reference=m_target,
                )
            else:
                if (
                    database.getTc(target.id, "post") is None
                    and database.isParentRole(target.id) is False
                ):
                    await message.channel.send(
                        "⚠ ロール **"
                        + target.name
                        + "** は、提出を指示する先のロールとしては登録されていません。"
                        + "もう一度、最初から操作をやり直してください。",
                        reference=m_target,
                    )
                else:
                    msg_ask_item = await message.channel.send(
                        "**"
                        + utils.roleIdToName(target.id, message.guild)
                        + "** に提出が指示された提出物は以下の通りです: \n"
                        + returnItemByRoleId(target.id, "all")
                        + "\n"
                        + "提出状況を確認したい提出先 ID を指定してください。",
                        reference=m_target,
                    )
                    try:
                        m_item_id = await client.wait_for(
                            "message", check=check, timeout=60
                        )
                    except asyncio.TimeoutError:
                        await message.channel.send(
                            "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。"
                            + "もう一度、最初から操作をやり直してください。",
                            reference=msg_ask_item,
                        )
                    else:
                        item_id = m_item_id.content

                        if item_id.isdigit():
                            fmt_check_list = ""
                            target_list = []
                            if database.isParentRole(target.id):
                                for role in database.getChildRole(target.id):
                                    target_list.append(str(role.id))
                            else:
                                target_list.append(database.getItemTarget(item_id))

                            for target in target_list:
                                fmt_check_list += utils.roleIdToName(
                                    target, message.guild
                                )
                                fmt_check_list += ": "

                                submit = database.getSubmitList(item_id, target)
                                if not submit:
                                    fmt_check_list += "❌\n"
                                else:
                                    fmt_check_list += "✅\n"

                            await message.channel.send(
                                ":notepad_spiral: 以下が提出先 **"
                                + database.getItemName(item_id)
                                + "** (対象: "
                                + utils.roleIdToName(
                                    database.getItemTarget(item_id), message.guild
                                )
                                + ") の提出状況です。\n\n"
                                + fmt_check_list,
                                reference=m_item_id,
                            )
                        else:
                            await message.channel.send(
                                "⚠ 提出先の指定方法が間違っています。提出状況を確認したい提出先 ID を番号で指定してください。"
                                + "もう一度、最初から操作をやり直してください。",
                                reference=m_item_id,
                            )


# sendNotify: 提出通知を送信する
async def sendNotify(submit_id, client, guild):
    submit = database.getSubmit(submit_id)
    if submit is None:
        print("[WARN] 提出通知の送信に失敗しました。")
    else:
        parent_role_id = database.getParentRole(submit.target)
        if parent_role_id is None:
            print(
                "[WARN] 通知用テキストチャンネルの取得に失敗したため、通知は行われませんでした。\n"
                + "       デバッグ情報:\n"
                + "       - submit_id: "
                + str(submit_id)
                + "\n"
                + "       - target: "
                + str(submit.target)
            )
            return
        notify_tc_id = database.getNotifyTc(parent_role_id)
        notify_tc = guild.get_channel(int(notify_tc_id))

        await notify_tc.send(
            "🔔 新しい提出があります。\n\n"
            + "🆔 提出 ID: "
            + str(submit.id)
            + "\n"
            + ":mailbox_closed: 提出先: "
            + database.getItemName(submit.item_id)
            + "\n"
            + ":alarm_clock: 提出日時: `"
            + utils.dtToStr(submit.datetime)
            + "`\n"
            + ":pencil2: 提出元ロール: "
            + utils.roleIdToName(submit.author_role, guild)
            + "\n"
            + ":person_juggling: 提出者: "
            + utils.userIdToName(client, submit.author)
            + "\n"
        )

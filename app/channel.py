# -*- coding: utf-8 -*-

# 外部ライブラリ
import discord
import asyncio
from parse import *

# 内部関数
import database
import utils


# 新規ロールの初期化作業 (テキストチャンネルの作成, テキストチャンネルの登録, etc.)
async def initRoleInteract(client, message):
    if utils.isStaff(message.author, message.guild):
        await message.channel.send("📛 ロールの名前は何にしますか？", reference=message)

        def check(m):
            return m.channel == message.channel and m.author == message.author

        try:
            m_role_name = await client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await message.channel.send(
                "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", reference=message
            )
        else:
            parent_role_list = ""
            for role in database.getParentRoleList():
                parent_role_list += utils.roleIdToName(role.id, message.guild)
                parent_role_list += ", "
            await message.channel.send(
                ":detective: このロールを、どの親ロールに帰属させますか？\n"
                + "現在、ボットには以下の親ロールが登録されています:\n**"
                + parent_role_list[:-2]
                + "**\n____Discord のメンション機能を使用して、____親ロールを指定してください。",
                reference=m_role_name,
            )
            try:
                m_parent_role = await client.wait_for(
                    "message", check=check, timeout=60
                )
            except asyncio.TimeoutError:
                await message.channel.send("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
            else:
                parent_role = utils.mentionToRoleId(m_parent_role.content)
                if not database.isParentRole(parent_role):
                    await message.channel.send(
                        "⚠ 指定したロールは親ロールとして登録されていません。\n" + "もう一度、最初から操作をやり直してください。",
                        reference=m_parent_role,
                    )
                else:
                    if (
                        discord.utils.get(
                            message.guild.categories,
                            id=int(database.getCategory("chat")),
                        )
                        is None
                    ):
                        await message.channel.send(
                            "⚠ チャット用チャンネルのカテゴリーが未設定か、または不正な値に設定されているため、処理を中断します。"
                        )
                    elif (
                        discord.utils.get(
                            message.guild.categories,
                            id=int(database.getCategory("post")),
                        )
                        is None
                    ):
                        await message.channel.send(
                            "⚠ 提出用チャンネルのカテゴリーが未設定か、または不正な値に設定されているため、処理を中断します。"
                        )
                    else:
                        if utils.isValidAsName(m_role_name.content) is False:
                            await message.channel.send(
                                "⚠ ロールの名前の指定方法が間違っています。もう一度、最初から操作をやり直してください。",
                                reference=m_role_name,
                            )
                        else:
                            role_name = m_role_name.content
                            await message.channel.send(
                                ":pick: ロール名 **" + role_name + "** で初期化処理を実行します...",
                                reference=m_parent_role,
                            )

                            # ロールを作る
                            guild = message.guild
                            role = await guild.create_role(name=role_name)

                            # ロールをデータベースに登録する
                            database.addRole(role.id, guild)

                            # テキストチャンネルの権限設定を定義する
                            ## @everyone の権限設定
                            ow_everyone = discord.PermissionOverwrite()
                            ow_everyone.view_channel = False
                            ## そのテキストチャンネルを使用するロールの権限設定
                            ow_target = discord.PermissionOverwrite()
                            ow_target.view_channel = True
                            ow_target.send_messages = True
                            ow_target.create_instant_invite = False
                            ow_target.read_messages = True
                            ow_target.read_message_history = True
                            ow_target.send_messages = True
                            ow_target.add_reactions = True
                            ow_target.attach_files = True
                            ow_target.mention_everyone = True
                            ow_target.send_tts_messages = False

                            # テキストチャンネルを作る
                            chat_category = discord.utils.get(
                                guild.categories, id=int(database.getCategory("chat"))
                            )
                            post_category = discord.utils.get(
                                guild.categories, id=int(database.getCategory("post"))
                            )
                            chat_channel = await guild.create_text_channel(
                                role_name,
                                category=chat_category,
                                topic="ロール "
                                + utils.roleIdToName(role.id, guild)
                                + " 向けの連絡用チャンネル",
                            )
                            post_channel = await guild.create_text_channel(
                                role_name,
                                category=post_category,
                                topic="ロール "
                                + utils.roleIdToName(role.id, guild)
                                + " 向けの提出用チャンネル",
                            )

                            # 委員会側の対応するロールを取得する
                            role_staff = guild.get_role(
                                database.getMemberToStaffRole(parent_role)
                            )

                            # テキストチャンネルの権限を設定する
                            await chat_channel.set_permissions(
                                role_staff, overwrite=ow_target
                            )
                            await chat_channel.set_permissions(
                                role, overwrite=ow_target
                            )
                            await chat_channel.set_permissions(
                                guild.default_role, overwrite=ow_everyone
                            )
                            await post_channel.set_permissions(
                                role, overwrite=ow_target
                            )
                            await post_channel.set_permissions(
                                guild.default_role, overwrite=ow_everyone
                            )

                            # テキストチャンネルをデータベースに登録する
                            database.setChatTc(role.id, chat_channel.id)
                            database.setPostTc(role.id, post_channel.id)

                            # 親ロールを設定する
                            database.setParentRole(role.id, parent_role)

                            await message.channel.send(
                                "✅ 処理が完了しました!", reference=m_parent_role
                            )
    else:
        await message.channel.send("⚠ このコマンドを実行する権限がありません。", reference=message)


# 特定のロールに関わる情報（提出物を除く）を削除する
async def pruneRoleInteract(client, message):
    if utils.isStaff(message.author, message.guild):
        msg_ask_role = await message.channel.send(
            "📛 ロールの情報と、それに関係するテキストチャンネルを削除したいロールを Discord の機能を用いてメンションしてください。",
            reference=message,
        )
        guild = message.guild

        def check(m):
            return m.channel == message.channel and m.author == message.author

        try:
            msg = await client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await message.channel.send(
                "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", reference=msg_ask_role
            )
        else:
            if utils.mentionToRoleId(msg.content) is None:
                await message.channel.send(
                    "⚠ ロールの指定方法が間違っています。Discord のメンション機能を用いてロールを指定してください。\n"
                    + "もう一度、最初から操作をやり直してください。",
                    reference=msg,
                )
            else:
                target = guild.get_role(int(utils.mentionToRoleId(msg.content)))

                if target is None:
                    await message.channel.send(
                        "⚠ 対象のロールが見つかりませんでした。指定しているロールが本当に正しいか、再確認してください。\n"
                        + "もう一度、最初から操作をやり直してください。",
                        reference=msg,
                    )
                else:
                    msg_ask_confirm = await message.channel.send(
                        ":cold_face: 本当にロール **"
                        + target.name
                        + "** を削除しますか？\n"
                        + "続行する場合は `y` と、キャンセルする場合は `n` と発言してください。",
                        reference=msg,
                    )
                    try:
                        msg_confirm = await client.wait_for(
                            "message", check=check, timeout=60
                        )
                    except asyncio.TimeoutError:
                        await message.channel.send(
                            "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。",
                            reference=msg_ask_confirm,
                        )
                    else:
                        if msg_confirm.content == "y":
                            await message.channel.send(
                                ":pick: ロール **" + target.name + "** の削除を処理しています...",
                                reference=msg_confirm,
                            )

                            # テキストチャンネルの削除
                            ## テキストチャンネルの取得
                            chat_tc = guild.get_channel(
                                database.getTc(target.id, "chat")
                            )
                            post_tc = guild.get_channel(
                                database.getTc(target.id, "post")
                            )

                            ## 削除の実行
                            if chat_tc is None:
                                await message.channel.send(
                                    ":information_source: チャット用テキストチャンネルは既に削除されています。このテキストチャンネルの削除はスキップされます。",
                                    reference=msg_confirm,
                                )
                            else:
                                await chat_tc.delete()

                            if chat_tc is None:
                                await message.channel.send(
                                    ":information_source: 提出用テキストチャンネルは既に削除されています。このテキストチャンネルの削除はスキップされます。",
                                    reference=msg_confirm,
                                )
                            else:
                                await post_tc.delete()

                            # データベース上からのロールの削除
                            if database.delRole(target.id, guild) is False:
                                await message.channel.send(
                                    ":information_source: データベース上のロールは既に削除されています。この処理はスキップされます。",
                                    reference=msg_confirm,
                                )

                            # Discord 上からのロールの削除
                            if target is None:
                                await message.channel.send(
                                    ":information_source: Discord 上のロールは既に削除されています。この処理はスキップされます。",
                                    reference=msg_confirm,
                                )
                            else:
                                await target.delete()

                            await message.channel.send(
                                "✅ ロール **" + target.name + "** の削除が完了しました。",
                                reference=msg_confirm,
                            )

                        else:
                            await message.channel.send(
                                ":congratulations: ロール **"
                                + target.name
                                + "** の削除をキャンセルしました。",
                                reference=msg_confirm,
                            )
    else:
        await message.channel.send("⚠ このコマンドを実行する権限がありません。")


async def setStaffRole(message):
    # サーバーの管理者権限を持っているか確認する
    if message.author.guild_permissions.administrator:
        # コマンドを解釈する
        response = parse("!role set staff <@&{}>", message.content)
        if response:
            # ロールが存在しないとき
            if message.guild.get_role(int(response[0])) is None:
                await message.channel.send(
                    "⚠ ロールの指定方法が間違っています。Discord のメンション機能を用いてロールを指定してください。\n"
                    + "もう一度、最初から操作をやり直してください。",
                    reference=message,
                )
            else:
                result = database.setStaffRole(response[0])
                if result:
                    await message.channel.send(
                        "✅ スタッフ用ロールを **"
                        + message.guild.get_role(int(response[0])).name
                        + "** に設定しました。",
                        reference=message,
                    )
                else:
                    await message.channel.send(
                        "⚠ 処理中になんらかの問題が発生しました。", reference=message
                    )
        else:
            await message.channel.send("❌ コマンドが不正です。", reference=message)
    else:
        await message.channel.send("⚠ このコマンドを実行する権限がありません。", reference=message)


async def setParentRole(client, message):
    if utils.isStaff(message.author, message.guild):
        await message.channel.send(
            "📛 どのロールの親ロールを変更しますか？\n" + "__Discord のメンション機能を使用して、__ロールを指定してください。",
            reference=message,
        )

        def check(m):
            return m.channel == message.channel and m.author == message.author

        try:
            msg_role = await client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await message.channel.send(
                "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", reference=message
            )
        else:
            role_id = utils.mentionToRoleId(msg_role.content)
            if role_id is None:
                await message.channel.send(
                    "⚠ ロールの指定方法が間違っています。\n"
                    + "__Discord のメンション機能を使用して、__ロールを指定してください。\n"
                    + "もう一度、最初から操作をやり直してください。",
                    reference=msg_role,
                )
            else:
                if not database.isParentRole(role_id):
                    role_name = utils.roleIdToName(role_id, message.guild)
                    if role_name is None:
                        await message.channel.send(
                            "⚠ 指定したロールは Discord 上に存在しません。\n" + "もう一度、最初から操作をやり直してください。",
                            reference=msg_role,
                        )
                    else:
                        msg_ask_dest = await message.channel.send(
                            ":detective: 親ロールの変更先はどちらにしますか？\n", reference=msg_role
                        )
                        try:
                            msg_parent_role = await client.wait_for(
                                "message", check=check, timeout=60
                            )
                        except asyncio.TimeoutError:
                            await message.channel.send(
                                "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。",
                                reference=msg_ask_dest,
                            )
                        else:
                            # 目的のユーザーが持つ親ロールを一旦全部剥がす
                            ## ボットに登録されている親ロールをすべて取得
                            parent_role_id = utils.mentionToRoleId(
                                msg_parent_role.content
                            )
                            parent_role_name = utils.roleIdToName(
                                parent_role_id, message.guild
                            )
                            if parent_role_name:
                                database.setParentRole(role_id, parent_role_id)
                                await message.channel.send(
                                    "✅ ロール **"
                                    + role_name
                                    + "** の親ロールを **"
                                    + parent_role_name
                                    + "** に変更しました。",
                                    reference=msg_parent_role,
                                )
                            else:
                                await message.channel.send(
                                    "⚠ 指定した親ロールは未登録か、ロールの指定方法が間違っています。\n"
                                    + "もう一度、最初から操作をやり直してください。",
                                    reference=msg_parent_role,
                                )
                else:
                    await message.channel.send(
                        "⚠ 指定したロールは親ロールです。親ロールに親ロールを指定することはできません。", reference=msg_role
                    )

    else:
        await message.channel.send("⚠ このコマンドを実行する権限がありません。", reference=message)


async def setChat(message):
    if utils.isStaff(message.author, message.guild):
        response = parse("!ch set chat <@&{}>", message.content)
        if response:
            result = database.setChatTc(response[0], message.channel.id)
            if result:
                await message.channel.send(
                    "✅ ロール **"
                    + message.guild.get_role(int(response[0])).name
                    + "** のチャット用チャンネルを設定しました。",
                    reference=message,
                )
            else:
                await message.channel.send(
                    "⚠ ロール **"
                    + message.guild.get_role(int(response[0])).name
                    + "** はまだボットに登録されていません。先に `!add role` コマンドを用いてボットにロールを登録してください。",
                    reference=message,
                )
        else:
            await message.channel.send("❌ コマンドが不正です。", reference=message)
    else:
        await message.channel.send("⚠ このコマンドを実行する権限がありません。", reference=message)


async def setChatCategory(message):
    if utils.isStaff(message.author, message.guild):
        response = parse("!cat set chat {}", message.content)
        if response:
            if response[0].isdigit():
                category = discord.utils.get(
                    message.guild.categories, id=int(response[0])
                )
                if category is not None:
                    database.setChatCategory(category.id)
                    await message.channel.send(
                        "✅ チャット用のチャンネル カテゴリーを **" + category.name + "** に設定しました。",
                        reference=message,
                    )
                else:
                    await message.channel.send(
                        "⚠ チャンネル カテゴリーの ID を正確に指定してください。\n" + "もう一度、最初から操作をやり直してください。",
                        reference=message,
                    )
            else:
                await message.channel.send(
                    "⚠ チャンネル カテゴリーの ID を正確に指定してください。\n" + "もう一度、最初から操作をやり直してください。",
                    reference=message,
                )
        else:
            await message.channel.send("❌ コマンドが不正です。", reference=message)
    else:
        await message.channel.send("⚠ このコマンドを実行する権限がありません。", reference=message)


async def setBotTc(message):
    if utils.isStaff(message.author, message.guild):
        channel = message.channel
        if channel is not None:
            database.setBotTc(channel.id)
            await message.channel.send(
                "✅ 管理用コマンドを実行するためのテキストチャンネルを **" + channel.name + "** に設定しました。",
                reference=message,
            )
        else:
            await message.channel.send(
                "⚠ 処理中に問題が発生しました。\n" + "もう一度、最初から操作をやり直してください。", reference=message
            )
    else:
        await message.channel.send("⚠ このコマンドを実行する権限がありません。", reference=message)


async def setPost(message):
    if utils.isStaff(message.author, message.guild):
        response = parse("!ch set post <@&{}>", message.content)
        if response:
            result = database.setPostTc(response[0], message.channel.id)
            if result:
                await message.channel.send(
                    "✅ ロール **"
                    + message.guild.get_role(int(response[0])).name
                    + "** の提出用チャンネルを設定しました。",
                    reference=message,
                )
            else:
                await message.channel.send(
                    "⚠ ロール **"
                    + message.guild.get_role(int(response[0])).name
                    + "** はまだボットに登録されていません。先に `!add role` コマンドを用いてボットにロールを登録してください。",
                    reference=message,
                )
        else:
            await message.channel.send(
                "❌ コマンドが不正です。\n" + "もう一度、最初から操作をやり直してください。", reference=message
            )
    else:
        await message.channel.send("⚠ このコマンドを実行する権限がありません。", reference=message)


async def setPostCategory(message):
    if utils.isStaff(message.author, message.guild):
        response = parse("!cat set post {}", message.content)
        if response:
            if response[0].isdigit():
                category = discord.utils.get(
                    message.guild.categories, id=int(response[0])
                )
                if category is not None:
                    database.setPostCategory(category.id)
                    await message.channel.send(
                        "✅ 提出用のチャンネル カテゴリーを **" + category.name + "** に設定しました。",
                        reference=message,
                    )
                else:
                    await message.channel.send(
                        "⚠ チャンネル カテゴリーの ID を正確に指定してください。\n" + "もう一度、最初から操作をやり直してください。",
                        reference=message,
                    )
            else:
                await message.channel.send(
                    "⚠ チャンネル カテゴリーの ID を正確に指定してください。\n" + "もう一度、最初から操作をやり直してください。",
                    reference=message,
                )
        else:
            await message.channel.send("❌ コマンドが不正です。", reference=message)
    else:
        await message.channel.send("⚠ このコマンドを実行する権限がありません。", reference=message)


async def setNotifyCategory(message):
    if utils.isStaff(message.author, message.guild):
        response = parse("!cat set notify {}", message.content)
        if response:
            if response[0].isdigit():
                category = discord.utils.get(
                    message.guild.categories, id=int(response[0])
                )
                if category is not None:
                    database.setNotifyCategory(category.id)
                    await message.channel.send(
                        "✅ 通知用のチャンネル カテゴリーを **" + category.name + "** に設定しました。",
                        reference=message,
                    )
                else:
                    await message.channel.send(
                        "⚠ チャンネル カテゴリーの ID を正確に指定してください。\n" + "もう一度、最初から操作をやり直してください。",
                        reference=message,
                    )
            else:
                await message.channel.send(
                    "⚠ チャンネル カテゴリーの ID を正確に指定してください。\n" + "もう一度、最初から操作をやり直してください。",
                    reference=message,
                )
        else:
            await message.channel.send("❌ コマンドが不正です。", reference=message)
    else:
        await message.channel.send("⚠ このコマンドを実行する権限がありません。", reference=message)


async def addRole(message):
    if utils.isStaff(message.author, message.guild):
        response = parse("!role add <@&{}>", message.content)
        if response:
            result = database.addRole(response[0], message.guild)
            if result:
                await message.channel.send(
                    "✅ ロール "
                    + message.guild.get_role(int(response[0])).name
                    + " をボットに登録しました。",
                    reference=message,
                )
            else:
                await message.channel.send(
                    "⚠ 指定されたロール **"
                    + message.guild.get_role(int(response[0])).name
                    + "** は既にボットに登録されています。",
                    reference=message,
                )
        else:
            await message.channel.send(
                "ボットにロールを追加できませんでした。コマンドを確認してください。\n" + "もう一度、最初から操作をやり直してください。",
                reference=message,
            )
    else:
        await message.channel.send("⚠ このコマンドを実行する権限がありません。", reference=message)


async def delRole(message):
    if utils.isStaff(message.author, message.guild):
        response = parse("!role delete <@&{}>", message.content)
        if response:
            result = database.delRole(response[0], message.guild)
            if result:
                await message.channel.send(
                    "✅ ロール **"
                    + message.guild.get_role(int(response[0])).name
                    + "** をボットから削除しました。",
                    reference=message,
                )
            else:
                await message.channel.send(
                    "⚠ 指定されたロール **"
                    + message.guild.get_role(int(response[0])).name
                    + "** はボットに登録されていません。",
                    reference=message,
                )
        else:
            await message.channel.send(
                "ボットからロールを削除できませんでした。コマンドを確認してください。", reference=message
            )
    else:
        await message.channel.send("⚠ このコマンドを実行する権限がありません。", reference=message)


async def showRole(message):
    if utils.isStaff(message.author, message.guild):
        role_id = database.getRole(message.channel.id)
        if role_id is None:
            await message.channel.send(
                "<#"
                + str(message.channel.id)
                + "> に紐付けられているロールはありません。\n"
                + "手動で紐付けるには、`!role add` コマンドを実行します。",
                reference=message,
            )
        else:
            await message.channel.send(
                "<#"
                + str(message.channel.id)
                + "> に紐付けられているロールは **"
                + utils.roleIdToName(role_id, message.guild)
                + "** です。",
                reference=message,
            )
    else:
        await message.channel.send("⚠ このコマンドを実行する権限がありません。", reference=message)


async def addParentRoleInteract(client, message):
    msg_ask_role = await message.channel.send(
        "📛 どのロールを親ロールとして登録しますか？\n"
        + "__Discord のメンション機能を使用して、__ロールを指定してください。\n"
        + "**親ロールの登録については、出店者側よりも先に委員会側の親ロールをボットに登録してください！**",
        reference=message,
    )

    def check(m):
        return m.channel == message.channel and m.author == message.author

    try:
        msg_role = await client.wait_for("message", check=check, timeout=60)
    except asyncio.TimeoutError:
        await message.channel.send(
            "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", reference=msg_ask_role
        )
    else:
        role_id = utils.mentionToRoleId(msg_role.content)
        if role_id is None:
            await message.channel.send(
                "⚠ ロールの指定方法が間違っています。\n"
                + "__Discord のメンション機能を使用して、__ロールを指定してください。\n"
                + "もう一度、最初から操作をやり直してください。",
                reference=msg_role,
            )
        else:
            if database.isParentRole(role_id):
                await message.channel.send(
                    "⚠ 指定されたロールは既に親ロールとして登録されています。", reference=msg_role
                )
            else:
                role_name = utils.roleIdToName(role_id, message.guild)
                if role_name is None:
                    await message.channel.send(
                        "⚠ 指定されたロールは Discord 上に存在しません。\n" + "もう一度、最初から操作をやり直してください。",
                        reference=msg_role,
                    )
                else:
                    msg_ask_type = await message.channel.send(
                        "親ロール **"
                        + role_name
                        + "** を、委員会 または 出店者のどちらとして登録しますか？\n"
                        + "委員会の場合は `staff`、出店者の場合は `member` と返信してください。",
                        reference=msg_role,
                    )
                    try:
                        msg_role_type = await client.wait_for(
                            "message", check=check, timeout=60
                        )
                    except asyncio.TimeoutError:
                        await message.channel.send(
                            "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。",
                            reference=msg_ask_type,
                        )
                    else:
                        role_type = msg_role_type.content

                        if role_type == "staff":
                            result = database.addParentRole(
                                role_id, msg_role_type.content, None, None
                            )
                            if result:
                                await message.channel.send(
                                    "✅ 親ロール **"
                                    + role_name
                                    + "** を 区別 **委員会** としてボットに登録しました。",
                                    reference=msg_role_type,
                                )
                            else:
                                await message.channel.send(
                                    "⚠ 処理中に問題が発生しました。\n" + "もう一度、最初から操作をやり直してください。"
                                )
                        elif role_type == "member":
                            msg_ask_staff_role = await message.channel.send(
                                "親ロール **"
                                + role_name
                                + "** を管理するのはどの委員会側の親ロールですか？\n"
                                + "Discord のメンション機能を使用して、親ロールを指定してください。",
                                reference=msg_role_type,
                            )
                            try:
                                msg_parent_role_manager = await client.wait_for(
                                    "message", check=check, timeout=60
                                )
                            except asyncio.TimeoutError:
                                await message.channel.send(
                                    "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。",
                                    reference=msg_ask_staff_role,
                                )
                            else:

                                if utils.isStaffRole(
                                    utils.mentionToRoleId(
                                        msg_parent_role_manager.content
                                    )
                                ):
                                    parent_role_manager = discord.utils.get(
                                        message.guild.roles,
                                        id=utils.mentionToRoleId(
                                            msg_parent_role_manager.content
                                        ),
                                    )
                                    # テキストチャンネルの権限設定を定義する
                                    ## @everyone の権限設定
                                    ow_everyone = discord.PermissionOverwrite()
                                    ow_everyone.view_channel = False
                                    ## そのテキストチャンネルを使用するロールの権限設定
                                    ow_target = discord.PermissionOverwrite()
                                    ow_target.view_channel = True
                                    ow_target.send_messages = False
                                    ow_target.create_instant_invite = False
                                    ow_target.read_messages = True
                                    ow_target.read_message_history = True
                                    ow_target.add_reactions = False
                                    ow_target.attach_files = False
                                    ow_target.mention_everyone = False
                                    ow_target.send_tts_messages = False

                                    if database.getCategory("notify") is None:
                                        await message.channel.send(
                                            "⚠ 通知用テキストチャンネルを作成するためのカテゴリーが未設定のため、処理を続行できません。"
                                        )
                                    else:
                                        # テキストチャンネルを作る
                                        notify_category = discord.utils.get(
                                            message.guild.categories,
                                            id=int(database.getCategory("notify")),
                                        )
                                        notify_tc = (
                                            await message.guild.create_text_channel(
                                                role_name,
                                                category=notify_category,
                                                topic="親ロール "
                                                + parent_role_manager.name
                                                + " に帰属するロールの提出通知がここに届きます。",
                                            )
                                        )

                                        # テキストチャンネルの権限を設定する
                                        await notify_tc.set_permissions(
                                            parent_role_manager, overwrite=ow_target
                                        )
                                        await notify_tc.set_permissions(
                                            message.guild.default_role,
                                            overwrite=ow_everyone,
                                        )

                                        staff_role = utils.mentionToRoleId(
                                            msg_parent_role_manager.content
                                        )
                                        result = database.addParentRole(
                                            role_id,
                                            msg_role_type.content,
                                            staff_role,
                                            notify_tc.id,
                                        )
                                        if result:
                                            await message.channel.send(
                                                "✅ 親ロール **"
                                                + role_name
                                                + "** を 区別 **出店者** としてボットに登録しました。",
                                                reference=msg_parent_role_manager,
                                            )
                                        else:
                                            await message.channel.send(
                                                "⚠ 処理中に問題が発生しました。\n"
                                                + "もう一度、最初から操作をやり直してください。"
                                            )
                                else:
                                    await message.channel.send(
                                        "⚠ 指定されたロールは、委員会側の親ロールではありません。\n"
                                        + "もう一度、最初から操作をやり直してください。",
                                        reference=msg_parent_role_manager,
                                    )
                        else:
                            await message.channel.send(
                                "⚠ ロールの区別の指定方法が間違っています。\n"
                                + "委員会の場合は `staff`、出店者の場合は `member` と返信してください。\n"
                                + "もう一度、最初から操作をやり直してください。",
                                reference=msg_role_type,
                            )


async def deleteParentRoleInteract(client, message):
    msg_ask_role = await message.channel.send(
        "📛 どのロールを親ロールの登録から削除しますか？\n" + "__Discord のメンション機能を使用して、__ロールを指定してください。\n",
        reference=message,
    )

    def check(m):
        return m.channel == message.channel and m.author == message.author

    try:
        msg_role = await client.wait_for("message", check=check, timeout=60)
    except asyncio.TimeoutError:
        await message.channel.send(
            "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", reference=msg_ask_role
        )
    else:
        role_id = utils.mentionToRoleId(msg_role.content)
        if role_id is None:
            await message.channel.send(
                "⚠ ロールの指定方法が間違っています。\n"
                + "__Discord のメンション機能を使用して、__ロールを指定してください。\n"
                + "もう一度、最初から操作をやり直してください。",
                reference=msg_role,
            )
        else:
            role_name = utils.roleIdToName(role_id, message.guild)
            if role_name is None:
                await message.channel.send(
                    "⚠ 指定されたロールは Discord 上に存在しません。\n" + "もう一度、最初から操作をやり直してください。",
                    reference=msg_role,
                )
            else:
                if database.isParentRole(role_id):
                    database.delParentRole(role_id)
                    await message.channel.send(
                        "✅ ロール **" + role_name + "** を親ロールの登録から削除しました。",
                        reference=msg_role,
                    )
                else:
                    await message.channel.send(
                        "⚠ 指定されたロールは親ロールとしてボットに登録されていません。", reference=msg_role
                    )


# setGuild(message):
async def setGuild(client, message):
    if utils.isStaff(message.author, message.guild):
        msg_ask_confirm = await message.channel.send(
            "❓ 本当にサーバー **"
            + str(message.guild)
            + "** をボットを使用するサーバーとして設定しますか？\n"
            + "続行する場合は `y`、キャンセルする場合は `n` と返信してください。",
            reference=message,
        )

        def check(m):
            return m.channel == message.channel and m.author == message.author

        try:
            msg_confirm = await client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await message.channel.send(
                "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。", reference=msg_ask_confirm
            )
        else:
            if msg_confirm.content == "y":
                database.setGuild(message.guild.id)
                await message.channel.send(
                    "✅ サーバー **" + str(message.guild) + "** をボットを使用するサーバーとして設定しました。",
                    reference=msg_role,
                )
            else:
                await message.channel.send("キャンセルしました。", reference=msg_role)
    else:
        await message.channel.send(
            "⚠ あなたはサーバー **"
            + str(message.guild)
            + "** の管理者権限を持っていないため、この操作を実行することはできません。"
        )


# autoRole(before, after): ロールの自動付与を処理する
async def autoRole(client, before, after):
    guild_id = database.getGuild()
    if guild_id:
        guild = client.get_guild(int(guild_id))
        if guild is None:
            print("[WARN] ボットを使用するサーバーの設定が間違っています。修正してください！")
        else:
            # 親ロール追加
            if before.roles == [guild.default_role]:
                tmp_roles = after.roles
                tmp_roles.pop(0)
                if database.isParentRole(tmp_roles[0].id) is False:
                    roles = database.getRoles()
                    isChildRole = False
                    for role in roles:
                        if role.id == tmp_roles[0].id:
                            isChildRole = True
                    if isChildRole:
                        parent_role = guild.get_role(
                            database.getParentRole(tmp_roles[0].id)
                        )
                        if parent_role is None:
                            pass
                        else:
                            await after.add_roles(parent_role)
    else:
        print("[WARN] ボットを使用するサーバーを設定してください！")

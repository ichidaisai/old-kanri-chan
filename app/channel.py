# -*- coding: utf-8 -*-

# 外部ライブラリ
import discord
from parse import *

# 内部関数
import database
import utils


# 新規ロールの初期化作業 (テキストチャンネルの作成, テキストチャンネルの登録, etc.)
async def initRoleInteract(client, message):
    await message.channel.send("📛 ロールの名前は何にしますか？")
    
    def check(m):
        return m.channel == message.channel and m.author == message.author

    try:
        m_role_name = await client.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        await message.channel.send("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
    else:
        
        if discord.utils.get(message.guild.categories, id=int(database.getCategory("chat"))) is None:
            await message.channel.send("⚠ チャット用チャンネルのカテゴリーが未設定か、または不正な値に設定されているため、処理を中断します。")
        elif discord.utils.get(message.guild.categories, id=int(database.getCategory("post"))) is None:
            await message.channel.send("⚠ 提出用チャンネルのカテゴリーが未設定か、または不正な値に設定されているため、処理を中断します。")
        else:
            role_name = m_role_name.content
            await message.channel.send(":pick: ロール名 **" + role_name + "** で初期化処理を実行します...")
            
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
            ow_target.mention_everyone = False
            ow_target.send_tts_messages = False
            
            # テキストチャンネルを作る
            chat_category = discord.utils.get(guild.categories, id=int(database.getCategory("chat")))
            post_category = discord.utils.get(guild.categories, id=int(database.getCategory("post")))
            chat_channel = await guild.create_text_channel(role_name, category=chat_category)
            post_channel = await guild.create_text_channel(role_name, category=post_category)
            
            # テキストチャンネルの権限を設定する
            await chat_channel.set_permissions(role, overwrite=ow_target)
            await chat_channel.set_permissions(guild.default_role, overwrite=ow_everyone)
            await post_channel.set_permissions(role, overwrite=ow_target)
            await post_channel.set_permissions(guild.default_role, overwrite=ow_everyone)
            
            # テキストチャンネルをデータベースに登録する
            database.setChatTc(role.id, chat_channel.id)
            database.setPostTc(role.id, post_channel.id)
            
            await message.channel.send("✅ 処理が完了しました!")
        
        

async def setChat(message):
    response = parse("!set chat <@&{}>", message.content)
    if response:
        result = database.setChatTc(response[0], message.channel.id)
        if result:
            await message.channel.send(
                "✅ ロール **"
                + message.guild.get_role(int(response[0])).name
                + "** のチャット用チャンネルを設定しました。"
            )
        else:
            await message.channel.send(
                "⚠ ロール **"
                + message.guild.get_role(int(response[0])).name
                + "** はまだボットに登録されていません。先に `!add role` コマンドを用いてボットにロールを登録してください。"
            )
    else:
        await message.channel.send("❌ コマンドが不正です。")

async def setChatCategory(message):
    response = parse("!cat set chat {}", message.content)
    if response:
        if response[0].isdigit():
            category = discord.utils.get(message.guild.categories, id=int(response[0]))
            if category is not None:
                database.setChatCategory(category.id)
                await message.channel.send(
                    "✅ チャット用のチャンネル カテゴリーを **"
                    + category.name
                    + "** に設定しました。"
                )
            else:
                await message.channel.send("⚠ チャンネル カテゴリーの ID を正確に指定してください。")
        else:
            await message.channel.send("⚠ チャンネル カテゴリーの ID を正確に指定してください。")
    else:
        await message.channel.send("❌ コマンドが不正です。")


async def setPost(message):
    response = parse("!set post <@&{}>", message.content)
    if response:
        result = database.setPostTc(response[0], message.channel.id)
        if result:
            await message.channel.send(
                "✅ ロール **"
                + message.guild.get_role(int(response[0])).name
                + "** の提出用チャンネルを設定しました。"
            )
        else:
            await message.channel.send(
                "⚠ ロール **"
                + message.guild.get_role(int(response[0])).name
                + "** はまだボットに登録されていません。先に `!add role` コマンドを用いてボットにロールを登録してください。"
            )
    else:
        await message.channel.send("❌ コマンドが不正です。")


async def setPostCategory(message):
    response = parse("!cat set post {}", message.content)
    if response:
        if response[0].isdigit():
            category = discord.utils.get(message.guild.categories, id=int(response[0]))
            if category is not None:
                database.setPostCategory(category.id)
                await message.channel.send(
                    "✅ 提出用のチャンネル カテゴリーを **"
                    + category.name
                    + "** に設定しました。"
                )
            else:
                await message.channel.send("⚠ チャンネル カテゴリーの ID を正確に指定してください。")
        else:
            await message.channel.send("⚠ チャンネル カテゴリーの ID を正確に指定してください。")
    else:
        await message.channel.send("❌ コマンドが不正です。")

async def addRole(message):
    response = parse("!add role <@&{}>", message.content)
    if response:
        result = database.addRole(response[0], message.guild)
        if result:
            await message.channel.send(
                "⚠ 指定されたロール **"
                + message.guild.get_role(int(response[0])).name
                + "** は既にボットに登録されています。"
            )
        else:

            await message.channel.send(
                "✅ ロール "
                + message.guild.get_role(int(response[0])).name
                + " をボットに登録しました。"
            )
    else:
        await message.channel.send("ボットにロールを追加できませんでした。コマンドを確認してください。")


async def delRole(message):
    response = parse("!del role <@&{}>", message.content)
    if response:
        result = database.delRole(response[0], message.guild)
        if result:
            await message.channel.send(
                "✅ ロール **"
                + message.guild.get_role(int(response[0])).name
                + "** をボットから削除しました。"
            )
        else:
            await message.channel.send(
                "⚠ 指定されたロール **"
                + message.guild.get_role(int(response[0])).name
                + "** はボットに登録されていません。"
            )
    else:
        await message.channel.send("ボットからロールを削除できませんでした。コマンドを確認してください。")


async def showRole(message):
    await message.channel.send(
        "<#"
        + str(message.channel.id)
        + "> に紐付けられているロールは **"
        + utils.roleIdToName(database.getRole(message.channel.id), message.guild)
        + "** です。"
    )

# -*- coding: utf-8 -*-

# 外部ライブラリ
import discord
from parse import *

# 内部関数
import database
import utils


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

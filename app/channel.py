# -*- coding: utf-8 -*-

# 外部ライブラリ
import discord
from parse import *

# 内部関数
import database


async def setChat(message):
    response = parse("!set chat <@&{}>", message.content)
    if response:
        database.setChatTc(response[0], message.channel.id)
        await message.channel.send(
            "ロール "
            + message.guild.get_role(int(response[0])).name
            + " のチャット用チャンネルを設定しました。"
        )
    else:
        await message.channel.send("コマンドが不正です。")


async def setPost(message):
    response = parse("!set post <@&{}>", message.content)
    if response:
        database.setPostTc(response[0], message.channel.id)
        await message.channel.send(
            "ロール "
            + message.guild.get_role(int(response[0])).name
            + " の提出用チャンネルを設定しました。"
        )
    else:
        await message.channel.send("コマンドが不正です。")


async def addRole(message):
    response = parse("!add role <@&{}>", message.content)
    if response:
        database.addRole(response[0], message.guild)
        await message.channel.send(
            "ロール " + message.guild.get_role(int(response[0])).name + " をボットに登録しました。"
        )
    else:
        await message.channel.send("ボットにロールを追加できませんでした。コマンドを確認してください。")


async def delRole(message):
    response = parse("!del role <@&{}>", message.content)
    if response:
        database.addRole(response[0], message.guild)
        await message.channel.send(
            "ロール " + message.guild.get_role(int(response[0])).name + " をボットから削除しました。"
        )
    else:
        await message.channel.send("ボットからロールを削除できませんでした。コマンドを確認してください。")


async def showRole(message):
    await message.channel.send(
        "<#"
        + str(message.channel.id)
        + "> に紐付けられているロールは <@&"
        + database.getRole(message.channel.id)
        + "> です。"
    )

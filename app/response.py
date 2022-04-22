# -*- coding: utf-8 -*-

# 外部ライブラリ
import discord

# 内部関数
import channel
import submission


async def doResp(message):
    if message.content.startswith("!add role"):
        await channel.addRole(message)
    if message.content.startswith("!del role"):
        await channel.delRole(message)
    elif message.content.startswith("!set chat"):
        await channel.setChat(message)
    elif message.content.startswith("!set post"):
        await channel.setPost(message)
    elif message.content.startswith("!add item"):
        await submission.addItem(message)
    elif message.content.startswith("!show role"):
        await channel.showRole(message)
    elif message.content.startswith("!show item"):
        await channel.showItem(message)
    else:
        pass

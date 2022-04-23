# -*- coding: utf-8 -*-

# 外部ライブラリ
import discord

# 内部関数
import channel
import submission


async def doResp(client, message):
    if message.content.startswith("!add role"):
        await channel.addRole(message)
    elif message.content.startswith("!del role"):
        await channel.delRole(message)
    elif message.content.startswith("!show role"):
        await channel.showRole(message)
    elif message.content.startswith("!set chat"):
        await channel.setChat(message)
    elif message.content.startswith("!set post"):
        await channel.setPost(message)
    elif message.content.startswith("!add item"):
        await submission.addItemInteract(client, message)
    elif message.content.startswith("!del item"):
        await submission.delItem(message)
    elif message.content.startswith("!show item"):
        await submission.showItem(message)
    elif message.attachments:
        await submission.submitItem(client, message)
    else:
        pass

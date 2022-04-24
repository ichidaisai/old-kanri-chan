# -*- coding: utf-8 -*-

# 外部ライブラリ
import discord

# 内部関数
import channel
import submission
import database


async def doResp(client, message):
    if message.content.startswith("!role add"):
        await channel.addRole(message)
    elif message.content.startswith("!role delete"):
        await channel.delRole(message)
    elif message.content.startswith("!role get"):
        await channel.showRole(message)
    elif message.content.startswith("!set chat"):
        await channel.setChat(message)
    elif message.content.startswith("!set post"):
        await channel.setPost(message)
    elif message.content.startswith("!item add"):
        await submission.addItemInteract(client, message)
    elif message.content.startswith("!item delete"):
        await submission.delItem(message)
    elif message.content.startswith("!item list"):
        await submission.showItem(message)
    elif message.attachments:
        if database.isPostTc(message.channel.id):
            await submission.submitFileItem(client, message)
    else:
        pass

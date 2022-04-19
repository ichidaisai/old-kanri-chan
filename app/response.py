# -*- coding: utf-8 -*-

# 外部ライブラリ
import discord

# 内部関数
import channel

async def doResp(message):
    if message.content.startswith("!add role"):
        await channel.addRole(message)
    elif message.content.startswith("!set chat"):
        await channel.setChat(message)
    elif message.content.startswith("!set post"):
        await channel.setPost(message)
    else:
        pass
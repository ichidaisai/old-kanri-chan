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
    elif message.content.startswith("!role parent add"):
        await channel.addParentRoleInteract(client, message)
    elif message.content.startswith("!role parent delete"):
        await channel.deleteParentRoleInteract(client, message)
    elif message.content.startswith("!role parent delete"):
        await channel.deleteParentRoleInteract(client, message)
    elif message.content.startswith("!role parent set"):
        await channel.setParentRole(client, message)
    elif message.content.startswith("!role init"):
        await channel.initRoleInteract(client, message)
    elif message.content.startswith("!role prune"):
        await channel.pruneRoleInteract(client, message)
    elif message.content.startswith("!role get"):
        await channel.showRole(message)
    elif message.content.startswith("!role set staff"):
        await channel.setStaffRole(message)
    elif message.content.startswith("!ch set chat"):
        await channel.setChat(message)
    elif message.content.startswith("!cat set chat"):
        await channel.setChatCategory(message)
    elif message.content.startswith("!cat set post"):
        await channel.setPostCategory(message)
    elif message.content.startswith("!ch set post"):
        await channel.setPost(message)
    elif message.content.startswith("!item add"):
        await submission.addItemInteract(client, message)
    elif message.content.startswith("!item delete"):
        await submission.delItem(message)
    elif message.content.startswith("!item list"):
        await submission.listItem(client, message)
    elif message.content.startswith("!submit list"):
        await submission.listSubmitInteract(client, message)
    elif message.content.startswith("!submit get"):
        await submission.getSubmitInteract(client, message)
    elif message.content.startswith("!plz"):
        await database.getUserParentRole(message)
    elif message.attachments:
        if database.isPostTc(message.channel.id):
            await submission.submitFileItem(client, message)
    else:
        pass

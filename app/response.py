# -*- coding: utf-8 -*-

# 外部ライブラリ
import discord
import unicodedata

# 内部関数
import channel
import submission
import database
import menu


async def doResp(client, message):
    message.content = unicodedata.normalize("NFKC", message.content)
    if message.content.startswith("!role add"):
        await channel.addRole(message)
    elif message.content.startswith("!menu") or message.content == "メニュー":
        ch_check = database.isChatTc(message.channel.id)
        if message.channel.id == database.getBotTc() or ch_check is False:
            await menu.showMenu(client, message)
        else:
            await message.channel.send("⚠ このチャンネルでボットを使用しないでください。\n提出用チャンネルに転送されます。")
            post_tc = client.get_channel(database.getTc(ch_check, "post"))
            message.channel = post_tc
            await menu.showMenu(client, message)
    elif message.content.startswith("!role delete"):
        await channel.delRole(message)
    elif message.content.startswith("!role parent add"):
        await channel.addParentRoleInteract(client, message)
    elif message.content.startswith("!role member set"):
        await channel.setMemberRole(message)
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
    elif message.content.startswith("!guild set"):
        await channel.setGuild(client, message)
    elif message.content.startswith("!cat set chat"):
        await channel.setChatCategory(message)
    elif message.content.startswith("!cat set post"):
        await channel.setPostCategory(message)
    elif message.content.startswith("!cat set notify"):
        await channel.setNotifyCategory(message)
    elif message.content.startswith("!ch set post"):
        await channel.setPost(message)
    elif message.content.startswith("!ch set bot"):
        await channel.setBotTc(message)
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
    elif message.content.startswith("!submit check"):
        await submission.checkSubmitInteract(client, message)
    elif message.content.startswith("!submit verify"):
        await submission.verifySubmitInteract(client, message)
    elif message.content == "提出":
        if database.isPostTc(message.channel.id):
            await submission.submitPlainTextInteract(client, message)
    elif message.attachments:
        if database.isPostTc(message.channel.id):
            await submission.submitFileItem(client, message)
    else:
        pass

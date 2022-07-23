# 内部関数
import asyncio
import database
import utils

from discord.ext import commands, tasks


@tasks.loop(seconds=5)
async def run(client):
    reminders = database.getReminder()
    guild_id = ""

    for reminder in reminders:
        submit_by_item_id = database.getSubmitList(reminder.item_id, None)
        already_submitted = []
        for author_role in submit_by_item_id:
            if submit_by_item_id.author_role is not None:
                already_submitted.append(submit_by_item_id.author_role)
        already_submitted = set(list(already_submitted))

        if reminder.target in already_submitted:
            print(
                "[INFO] 提出先 ID: "
                + reminder.item_id
                + ","
                + "対象ロール ID: "
                + reminder.target
                + " "
                + "に対する通知は、既に提出済みのため行われませんでした。"
            )
        else:
            tc_id = database.getTc(reminder.target, "chat")
            if guild_id == "":
                guild_id = database.getGuild()

            tc = client.get_guild(int(guild_id)).get_channel(int(tc_id))
            if tc is None:
                print(
                    "[WARN] テキストチャンネルの ID `"
                    + tc_id
                    + "` に対するスケジュール処理は行われませんでした。ロールまたはテキストチャンネルが存在しません。\n"
                    + "(上記に表示される tc_id は、空欄である可能性があります。)\n"
                )
            else:
                item_name = database.getItemName(reminder.item_id)
                item_limit = utils.dtToStr(database.getItemLimit(reminder.item_id))
                await tc.send(
                    "🔔 **"
                    + item_name
                    + "** の提出期限は `"
                    + item_limit
                    + "` ですが、まだ提出されていないようです。\n"
                    + "可能な限りの早めの提出をお願いします！"
                )
                database.delReminder(reminder.id)

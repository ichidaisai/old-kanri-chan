# 外部関数
import datetime
from datetime import timedelta

# 内部関数
import asyncio
import database
import utils

from discord.ext import commands, tasks


@tasks.loop(seconds=5)
async def run(client):
    reminders = database.getReminder()
    guild_id = database.getGuild()

    for reminder in reminders:
        submit_by_item_id = database.getSubmitList(reminder.item_id, None)
        already_submitted = []
        for submit in submit_by_item_id:
            if submit.author_role is not None:
                already_submitted.append(submit.author_role)
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
            database.delReminder(reminder.id)
        else:
            tc_id = database.getTc(reminder.target, "chat")

            if tc_id is None:
                print("[WARN] 次のロール ID のテキストチャンネルが設定されていません!: " + str(reminder.target))
                database.delReminder(reminder.id)
            else:
                tc = client.get_guild(int(guild_id)).get_channel(int(tc_id))
                if tc is None:
                    print(
                        "[WARN] テキストチャンネルの ID `"
                        + str(tc_id)
                        + "` に対するスケジュール処理は行われませんでした。ロールまたはテキストチャンネルが存在しません。\n"
                        + "(上記に表示される tc_id は、空欄である可能性があります。)\n"
                    )
                    database.delReminder(reminder.id)
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


### 毎週月曜日の10時に通知する
mon_noti = 0


@utils.static_vars(mon_noti=0)
@tasks.loop(seconds=1)
async def call_weekly_notify(client):
    dt_now = datetime.datetime.now()
    # 曜日を取得 (月曜日は 0)
    date = dt_now.weekday()
    # 通知する締切の範囲を示す。
    limit_date = datetime.datetime.now() + timedelta(days=7)
    # 月曜10時台に実行する。
    if date == 0 and dt_now.hour == 10:
        if dt_now.minute == 0 and call_weekly_notify.mon_noti == 0:
            await weekly_notify(client, limit_date)
            # 複数回実行されないようにする
            call_weekly_notify.mon_noti = 1
        elif mon_noti == 1 and dt_now.minute >= 5:  # 5分経過で変数を戻す
            call_weekly_notify.mon_noti = 0


async def weekly_notify(client, limit_date):
    guild_id = database.getGuild()
    roles = database.getMemberRoles()  # 出店者ロール一覧

    for role in roles:
        mon_noti_list = []  # 締切が1週間以内の提出物IDを格納
        reminders = database.getReminder(
            role.id, None
        )  # 指定した DiscordID,提出物ID のリマインダーをすべて返す
        for reminder in reminders:
            submit_by_item_id = database.getSubmitList(
                reminder.item_id, role.id
            )  # 提出先の ID と提出者のロール ID から、提出された項目のデータを返す
            already_submitted = []
            for submit in submit_by_item_id:
                if submit.author_role is not None:
                    already_submitted.append(submit.author_role)
            already_submitted = set(list(already_submitted))

            # 締切が1週間以内か確認する
            if reminder.datetime < limit_date:
                # 配列に提出物IDを追加する
                mon_noti_list.append(reminder.item_id)

        # 配列を基に、通知する。
        tc_id = database.getTc(role.id, "chat")
        tc = client.get_guild(int(guild_id)).get_channel(int(tc_id))

        # 提出物IDの重複を削除する
        mon_noti_list = list(set(mon_noti_list))

        if len(mon_noti_list) == 0:  # 提出物は無い場合
            msg = "✅ 今週が締切の提出物はありません\n"

            for reminder in reminders:
                msg += reminder.id + "\n"
            await tc.send(msg)
        else:  # 提出物がある場合
            msg = "⚠️ 今週が締切の提出物をお知らせします。\n"

            for item_id in mon_noti_list:
                item_name = database.getItemName(item_id)
                item_limit = utils.dtToStr(database.getItemLimit(reminder.item_id))
                msg += "📛 提出先: **" + item_name + "**, "
                msg += "⏰ 提出期限: `" + item_limit + "`\n"
            await tc.send(msg)

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
    guild_id = ""

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
            if guild_id == "":
                guild_id = database.getGuild()

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

@tasks.loop(minutes=1)
async def mon_notification(client):
    dt_now = datetime.datetime.now()
    # 曜日を取得(Mon:0)
    date = datetime.date(dt_now.year, dt_now.month, dt_now.day)
    # 通知する締切の範囲を示す。
    limit_date = datetime.now() + timedelta(days=7)
    # 月曜10時台に実行する。
    if date == 0 and dt_now.hour == 10 :
        if dt_now.minute == 0 and mon_noti == 0:
            Mon_notification(limit_date)
            print("通知の送信が完了しました")
            # 複数回実行されないようにする
            dt_now.minute = 1
        elif mon_noti == 1 and dt_now.minute >= 5: # 5分経過で変数を戻す
            dt_now.minute = 0


async def Mon_notification(client,limit_date):
    guild_id = ""
    author_role_list = database.getMemberRoles() # 出店者ロール一覧

    for author_role in author_role_list:
        mon_noti_list = [] # 締切が1週間以内の提出物IDを格納
        reminders = database.getReminder(author_role,None) # 指定した DiscordID,提出物ID のリマインダーをすべて返す
        for reminder in reminders:
            submit_by_item_id = database.getSubmitList(reminder.item_id, author_role) # 提出先の ID と提出者のロール ID から、提出された項目のデータを返す
            already_submitted = []
            for submit in submit_by_item_id:
                if submit.author_role is not None:
                    already_submitted.append(submit.author_role)
            already_submitted = set(list(already_submitted))

            # 提出済みの場合
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
            # 未提出の場合
            else: 
                # 締切が1週間以内か確認する
                if reminder.datetime < limit_date:
                    # 配列に提出物IDを追加する
                    mon_noti_list.append(reminder.id)
        
        # 配列を基に、通知する。
        tc_id = database.getTc(reminder.target, "chat")
        if guild_id == "":
                guild_id = database.getGuild()
        tc = client.get_guild(int(guild_id)).get_channel(int(tc_id))

        # 提出物IDの重複を削除する
        set(mon_noti_list)

        if len(mon_noti_list) == 0: # 提出物は無い場合
            await tc.send(
                "✅今週が締切の提出物はありません"
            )
        else: # 提出物がある場合
            # なんとかする
            await tc.send(
                "⚠️今週が締切の提出物をお知らせします"
            )
            for item_id in mon_noti_list:
                item_name = database.getItemName(item_id)
                item_limit = utils.dtToStr(database.getItemLimit(reminder.item_id))
                await tc.send(
                    "** 提出物名："
                    + item_name
                    + "**   締切: `"
                    + item_limit
                    + "`\n"
                )
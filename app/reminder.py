# 外部ライブラリ
import dateutil.parser

# 内部関数
import database
import utils
import asyncio
import submission


async def addReminderInteract(client, message):
    if utils.isStaff(message.author, message.guild):
        await message.channel.send(
            "📛 どのロールに指示された提出物のリマインダーを追加しますか？\n" + "Discord のメンション機能を使用して、ロールを指定してください。"
        )

        def check(m):
            return m.channel == message.channel and m.author == message.author

        try:
            m_role_name = await client.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await message.channel.send("⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。")
        else:
            if utils.mentionToRoleId(m_role_name.content) is None:
                await message.channel.send(
                    "⚠ ロールの指定方法が間違っています。Discord のメンション機能を用いてロールを指定してください。\n"
                    + "もう一度、最初から操作をやり直してください。"
                )
            else:
                target = message.guild.get_role(
                    int(utils.mentionToRoleId(m_role_name.content))
                )
                if target is None:
                    await message.channel.send(
                        "⚠ 対象のロールが見つかりませんでした。指定しているロールが本当に正しいか、再確認してください。\n"
                        + "もう一度、最初から操作をやり直してください。"
                    )
                else:
                    # if (
                    #     database.getTc(target.id, "post") is None
                    #     and database.isParentRole(target.id) is False
                    # ):
                    if utils.isStaffRole(target.id):
                        await message.channel.send(
                            "⚠ ロール **" + target.name + "** は、提出を指示する先のロールとしては登録されていません。"
                        )
                    else:
                        await message.channel.send(
                            "**"
                            + utils.roleIdToName(target.id, message.guild)
                            + "** に提出が指示された提出物は以下の通りです: \n"
                            + submission.returnItemByRoleId(target.id, "all")
                            + "\n目的の提出先 ID の提出先 ID をこのチャンネルで発言してください。"
                        )

                        def check(m):
                            return (
                                m.channel == message.channel
                                and m.author == message.author
                            )

                        try:
                            m_item_id = await client.wait_for(
                                "message", check=check, timeout=60
                            )
                        except asyncio.TimeoutError:
                            await message.channel.send(
                                "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。"
                            )
                        else:
                            item_name = database.getItemName(m_item_id.content)
                            if item_name is None:
                                await message.channel.send(
                                    "⚠ 指定された提出先は存在しません。もう一度、最初から操作をやり直してください。"
                                )
                            else:
                                await message.channel.send(
                                    "⏰ リマインダーを設定する日時はいつにしますか？"
                                    + "入力例: 2022年4月1日 21時30分 としたい場合は、`2022/4/1 21:30` と入力します。\n"
                                )
                                try:
                                    m_datetime = await client.wait_for(
                                        "message", check=check, timeout=60
                                    )
                                except asyncio.TimeoutError:
                                    await message.channel.send(
                                        "⚠ タイムアウトしました。もう一度、最初から操作をやり直してください。"
                                    )
                                else:
                                    if utils.isDateTime(m_datetime.content):
                                        reminder_datetime = dateutil.parser.parse(
                                            m_datetime.content
                                        )
                                        if database.isParentRole(target.id):
                                            for role in database.getChildRole(
                                                target.id
                                            ):
                                                database.addReminder(
                                                    int(m_item_id.content),
                                                    role.id,
                                                    reminder_datetime,
                                                )
                                        elif int(database.getMemberRole()) == target.id:
                                            roles = database.getMemberRoles()
                                            for role in roles:
                                                database.addReminder(
                                                    int(m_item_id.content),
                                                    role.id,
                                                    reminder_datetime,
                                                )
                                        else:
                                            database.addReminder(
                                                int(m_item_id.content),
                                                int(target.id),
                                                reminder_datetime,
                                            )
                                        await message.channel.send(
                                            "✅ リマインダーを追加しました。\n"
                                            + "📮 提出先: "
                                            + item_name
                                            + "\n"
                                            + "👤 対象者: "
                                            + target.name
                                            + "\n"
                                            + "⏰ リマインダー 日時: `"
                                            + utils.dtToStr(reminder_datetime)
                                            + "\n"
                                            + "`"
                                        )
                                    else:
                                        await message.channel.send(
                                            "⚠ 指定された期限をうまく解釈できませんでした。\n"
                                            + "入力例: 2022年4月1日 21時30分 としたい場合は、`2022/4/1 21:30` と入力します。\n"
                                            + "もう一度、最初から操作をやり直してください。"
                                        )
    else:
        await message.channel.send("⚠ このコマンドを実行する権限がありません。")

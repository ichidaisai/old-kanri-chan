# 外部ライブラリ
import discord

# 内部関数
import database
import channel
import utils
import submission
import reminder


class initButton(discord.ui.View):
    def __init__(self, args):
        super().__init__()

        for txt in args:
            self.add_item(doCommand(txt))


class doCommand(discord.ui.Button):
    used = False

    def __init__(self, txt: str):
        super().__init__(label=txt, style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        message = interaction.message
        message.author = interaction.user
        label = self.label
        client = interaction.client

        if not self.used:
            self.used = True
            # 提出先への提出、提出履歴の閲覧など、一般ユーザー向けの項目
            if label == "🏷️ 提出履歴を見る":
                await interaction.response.send_message("提出履歴を表示します...")
                await submission.listSubmitInteract(client, message)
            elif label == "💾 提出したファイルをダウンロードする" or label == "💾 提出されたファイルをダウンロードする":
                await interaction.response.send_message("提出したファイルのダウンロードをご案内します...")
                await submission.getSubmitInteract(client, message)
            elif label == "📜 プレーンテキストを提出する":
                await interaction.response.send_message("プレーンテキストの提出をご案内します...")
                await submission.submitPlainTextInteract(client, message)
            elif label == "📄 ファイルを提出する":
                await interaction.response.send_message(
                    "💡 ファイルを提出するには、提出用チャンネルでファイルをアップロードし、その後ボットの指示にしたがってください。"
                )
            # スタッフ向け
            ## 提出先の管理
            elif label == "➕ 提出先の作成":
                await interaction.response.send_message("提出先の作成をご案内します...")
                await submission.addItemInteract(client, message)
            elif label == "➖ 提出先の削除":
                await interaction.response.send_message("提出先の作成をご案内します...")
                await submission.delItemInteract(client, message)
            elif label == "📥 提出状況の確認":
                await interaction.response.send_message("提出状況の確認をご案内します...")
                await submission.checkSubmitInteract(client, message)
            elif label == "✅ 提出物の承認":
                await interaction.response.send_message("提出物の承認をご案内します...")
                await submission.verifySubmitInteract(client, message)
            ## リマインダーの管理
            elif label == "➕ リマインダーの追加":
                await interaction.response.send_message("リマインダーの追加をご案内します...")
                await reminder.addReminderInteract(client, message)
            ## ロールの管理
            elif label == "➕ ロールの作成":
                await interaction.response.send_message("ロールの作成をご案内します...")
                await channel.initRoleInteract(client, message)
            elif label == "➖ ロールの削除":
                await interaction.response.send_message("ロールの削除をご案内します...")
                await channel.pruneRoleInteract(client, message)
            else:
                await interaction.response.send_message(
                    "⚠ 処理中に問題が発生しました。\n" + "もう一度、最初から操作をやり直してください。"
                )
        else:
            await interaction.response.send_message(
                "⚠ このメニューは使用済みです。\n" + "もう一度、メニューを呼び出してください。"
            )


async def showMenu(client, message):
    await message.channel.send(":m: メニュー")

    if database.getBotTc() is None:
        print(
            "[WARN] 管理用コマンドを実行するためのテキストチャンネルを設定してください！\n"
            + "       `!ch set bot` コマンドを実行して設定できます。"
        )
    else:
        # スタッフ向け
        if message.channel.id == database.getBotTc():
            ## 提出先 / 提出物の管理
            args = [
                "➕ 提出先の作成",
                "➖ 提出先の削除",
                "📥 提出状況の確認",
                "✅ 提出物の承認",
                "🏷️ 提出履歴を見る",
                "💾 提出されたファイルをダウンロードする",
            ]
            await message.channel.send(
                ":open_file_folder: 提出先 / 提出物の管理について", view=initButton(args)
            )
            ## ロールの管理
            args = ["➕ ロールの作成", "➖ ロールの削除"]
            await message.channel.send(
                ":person_tipping_hand: ロールの管理について", view=initButton(args)
            )
            ## リマインダーの管理
            args = ["➕ リマインダーの追加"]
            await message.channel.send("⏰ リマインダーについて", view=initButton(args))
        else:
            # 提出先への提出、提出履歴の閲覧など、一般ユーザー向けの項目
            args = [
                "🏷️ 提出履歴を見る",
                "💾 提出したファイルをダウンロードする",
                "📜 プレーンテキストを提出する",
                "📄 ファイルを提出する",
            ]
            await message.channel.send(
                ":mailbox_closed: 提出物について", view=initButton(args)
            )

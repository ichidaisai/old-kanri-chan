# -*- coding: utf-8 -*-

# 外部ライブラリ
import discord
import sys
from parse import *
import asyncio

# 内部関数
import config
import response
import channel
import scheduler

# ボットのクライアントを定義
class MyClient(discord.Client):
    async def on_ready(self):
        # 提出のリマインダーのスケジューラを起動する
        scheduler.run.start(self)
        scheduler.call_weekly_notify.start(self)

        print(f"[INFO] {self.user} として Discord に接続しました。")

    # ユーザーのコマンド、メッセージ等を処理
    async def on_message(self, message):
        print("[INFO] [Received] " + message.author.name + ": " + message.content)
        await response.doResp(self, message)

    # ロールの自動付与を呼ぶ
    async def on_member_update(self, before, after):
        await channel.autoRole(self, before, after)


def main():
    # config.yml のトークン部分が正常なことを確認する
    if config.checkConfig():
        # 定義されたクライアントを読み込み、ボットを起動する
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        client = MyClient(intents=intents)
        client.run(config.getToken())
    else:
        print("config.yml の内容が正しくありません。終了します。")
        sys.exit(1)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-

# 外部ライブラリ
import discord
import sys
from parse import *

# 内部関数
import config
import database

# ボットのクライアントを定義
class MyClient(discord.Client):
    async def on_ready(self):
        print(f"[INFO] {self.user} として Discord に接続しました。")

    # ユーザーのコマンド、メッセージ等を処理
    async def on_message(self, message):

        if message.content.startswith("!add role"):
            response = parse("!add role <@&{}>", message.content)
            if response:
                database.addGroup(response[0], message.guild)
                await message.channel.send(
                    "ロール "
                    + message.guild.get_role(int(response[0])).name
                    + " をボットに登録しました。"
                )
            else:
                await message.channel.send("ボットにロールを追加できませんでした。コマンドを確認してください。")
        elif message.content.startswith("!set chat"):
            response = parse("!set chat <@&{}>", message.content)
            if response:
                database.setChatTc(response[0], message.channel.id)
                await message.channel.send(
                    "ロール "
                    + message.guild.get_role(int(response[0])).name
                    + " のチャット用チャンネルを設定しました。"
                )
            else:
                await message.channel.send("コマンドが不正です。")
        elif message.content.startswith("!set post"):
            response = parse("!set post <@&{}>", message.content)
            if response:
                database.setPostTc(response[0], message.channel.id)
                await message.channel.send(
                    "ロール "
                    + message.guild.get_role(int(response[0])).name
                    + " の提出用チャンネルを設定しました。"
                )
            else:
                await message.channel.send("コマンドが不正です。")
        else:
            pass


def main():
    # config.yml のトークン部分が正常なことを確認する
    if config.checkConfig():
        # 定義されたクライアントを読み込み、ボットを起動する
        client = MyClient()
        client.run(config.getToken())
    else:
        print(f"config.yml の内容が正しくありません。終了します。")
        sys.exit(1)


if __name__ == "__main__":
    main()

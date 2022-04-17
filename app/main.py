# -*- coding: utf-8 -*-

# 外部ライブラリ
import discord
import sys
from parse import *
from os.path import exists

# 内部関数
import config
import database

# ボットのクライアントを定義
class MyClient(discord.Client):
    async def on_ready(self):
        print(f'[INFO] {self.user} として Discord に接続しました。')
    
    # ユーザーのコマンド、メッセージ等を処理
    async def on_message(self, message):
        
        if (message.content.startswith('!add role')):
            response = parse("!add role <@&{}>", message.content)
            database.addGroup(response[0], message.guild)
        elif (message.content.startswith('!set chat')):
            response = parse("!set chat <@&{}>", message.content)
            database.setChatTc(response[0], message.channel.id)
            await message.channel.send("ロール " + message.guild.get_role(int(response[0])).name + " のチャット用チャンネルを設定しました。")
        elif (message.content.startswith('!set post')):
            response = parse("!set post <@&{}>", message.content)
            database.setPostTc(response[0], message.channel.id)
            await message.channel.send("ロール " + message.guild.get_role(int(response[0])).name + " の提出用チャンネルを設定しました。")
        else:
            print(f'[INFO] [Message log] {message.author}: {message.content}')
        

def main():
    # config.yml のトークン部分が正常なことを確認する
    if exists('./config.yml'):
        if config.getToken() == '':
            print(f'Discord のトークンが指定されていません。終了します。')
        else:
            # 定義されたクライアントを読み込み、ボットを起動する
            client = MyClient()
            client.run(config.getToken())
    else:
        print(f'[ERROR] 設定ファイル config.yml が存在しません。終了します。')
        sys.exit(1)

if __name__ == '__main__':
    main()
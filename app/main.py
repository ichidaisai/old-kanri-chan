# 外部ライブラリ
import discord
import sys
from os.path import exists

# 内部関数
import config

# ボットのクライアントを定義
class MyClient(discord.Client):
    async def on_ready(self):
        print(f'[INFO] {self.user} として Discord に接続しました。')
    
    # ユーザーのコマンド、メッセージ等を処理
    async def on_message(self, message):
        print(f'[test] {message.author}: {message.content}')

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
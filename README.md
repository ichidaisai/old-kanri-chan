# discord-bot-2022
2022年度 Discord ボット

## セットアップ方法
1. このリポジトリをクローンします。
2. リポジトリの直下に `config.yml` を `config.sample.yml` をコピーして作成します。
3. `docker-compose up -d` を実行します。

## コマンド チートシート
* ボットの動作ログを表示する
    ```shell
    docker-compose logs app
    ```
* ボットのソースコードの変更を反映して、再起動する
    ```shell
    docker-compose build && docker-compose up -d
    ```
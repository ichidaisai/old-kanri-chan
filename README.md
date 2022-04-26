# kanri-chan
広島市立大学 大学祭 Discord サーバー 管理用ボット\

**⚠注意: ** このボットは、複数のサーバーに参加して同時に運用されることを全く想定していません。そのような運用をせず、Discord サーバーごとにボットのインスタンスを用意してください！

## セットアップ方法
1. このリポジトリをクローンします。
2. リポジトリの直下に `config.yml` を `config.sample.yml` をコピーして作成します。
3. `docker-compose up -d` を実行します。

## 開発環境
1. `./utils/up.sh` を実行して、開発用コンテナを立ち上げます。
2. `./utils/attach.sh` を実行して、開発用アンテナのシェルに入ります。
3. `pip install -r requirements.txt` を実行して、前提となるライブラリをインストールします。
4. (初回のみ) `config.sample.yml` を `config.yml` としてコピーし、適宜値を編集します。
5. `python main.py` を実行して、ボットを起動します。

## コマンド チートシート
* ボットの動作ログを表示する
    ```shell
    docker-compose logs app
    ```
* ボットのソースコードの変更を反映して、再起動する
    ```shell
    docker-compose build && docker-compose up -d
    ```

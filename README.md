# kanri-chan
広島市立大学 大学祭 Discord サーバー 管理用ボット
#### ⚠ 注意
このボットは、複数のサーバーに参加して同時に運用されることを全く想定していません。そのような運用をせず、Discord サーバーごとにボットのインスタンスを用意してください！

## 導入する
* ここでは、`$HOME/kanri-chan` 配下にファイルを設置することを前提とします。
  * 他の場所に設置する場合は、適宜読み替えてください。
* 以下の作業の実行前に、あなたのサーバーに Docker と curl をインストールしてください。

### 1. 必要なファイルを配置する
* 以下のコマンドを実行してリポジトリからファイルをダウンロードします。
    ```shell
    mkdir -p data/posts
    curl -O https://raw.githubusercontent.com/ichidaisai/kanri-chan/main/docker-compose.yml
    curl -o data/config.yml https://raw.githubusercontent.com/ichidaisai/kanri-chan/main/data/config.sample.yml
    ```
### 2. ボットの Discord トークンを設定する
* `$HOME/kanri-chan/config.yml` を編集して、[Discord Developer Portal](https://discord.com/developers/applications) から入手できるトークンを設定します。
* ⚠ 注意
  * この際、アプリケーションのページから `Bot` を開き、以下のオプションを有効化します。行わない場合、サーバー上のメンバーの情報を正常に取得できず、一部の処理に失敗します。
    * Server Members Intent
    * Message Content Intent

### 3. ボットを起動する
* `docker-compose.yml` が存在するディレクトリに移動してから、以下のコマンドを実行します。
    ```shell
    docker compose up -d
    ```

## アップデート
* ボットの更新を適用するには、`docker-compose.yml` が存在するディレクトリに移動してから、以下のコマンドを実行します。
    ```shell
    docker compose pull
    docker compose up -d
    ```

## 開発する
* 以下の作業の実行前に、あなたのコンピュータに Docker と Git をインストールしてください。
### 1. リポジトリをクローンする
* 以下のコマンドを実行するか、またはその他の方法でこのリポジトリをクローンします。
    ```shell
    # https
    git clone https://github.com/ichidaisai/kanri-chan
    # or ssh
    # git clone git@github.com:ichidaisai/kanri-chan.git
    ```

### 2. 開発用コンテナを起動する
* 以下のコマンドをリポジトリ内で実行します。
    ```shell
    ./utils/up.sh
    ```

### 3. 開発用コンテナにアタッチする
* 以下のコマンドをリポジトリ内で実行します。
    ```shell
    ./utils/attach.sh
    ```

### 4. ボットの設定を行う
* `./data/config.sample.yml` を `./data/config.yml` としてコピーし、[Discord Developer Portal](https://discord.com/developers/applications) から入手できるトークンを設定します。
* ⚠ 注意
  * この際、アプリケーションのページから `Bot` を開き、以下のオプションを有効化します。行わない場合、サーバー上のメンバーの情報を正常に取得できず、一部の処理に失敗します。
    * Server Members Intent
    * Message Content Intent

### 5. 開発用のボットを起動する
* 以下のコマンドを、開発用コンテナにアタッチした状態で実行します。
    ```shell
    python main.py
    ```


## ライセンス
BSD 3-Clause "New" or "Revised" License
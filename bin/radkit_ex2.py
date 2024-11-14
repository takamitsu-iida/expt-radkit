#!/usr/bin/env python
"""RADKit Pythonスクリプト

"""

#
# 標準ライブラリのインポート
#
import logging
import sys
from pathlib import Path

import webbrowser
import json

#
# サードパーティライブラリのインポート
#
from websocket import create_connection

try:
    from radkit_client.sync import Client
except ImportError:
    logging.error('radkit_clientが見つかりません。')
    print(sys.path)
    sys.exit(1)

try:
    import radkit_genie
except ImportError:
    logging.error('radkit_genieが見つかりません。')
    print(sys.path)
    sys.exit(1)

# このファイルへのPathオブジェクト
app_path = Path(__file__)

# このファイルの名前から拡張子を除いてプログラム名を得る
app_name = app_path.stem

# アプリケーションのホームディレクトリはこのファイルからみて一つ上
app_home = app_path.parent.joinpath('..').resolve()

# データ用ディレクトリ
data_dir = app_home.joinpath('data')

# libフォルダにおいたpythonスクリプトをインポートできるようにするための処理
# このファイルの位置から一つ
lib_dir = app_home.joinpath('lib')
if lib_dir not in sys.path:
    sys.path.append(str(lib_dir))

#
# ログ設定
#

# ログファイルの名前
log_file = app_path.with_suffix('.log').name

# ログファイルを置くディレクトリ
log_dir = app_home.joinpath('log')
log_dir.mkdir(exist_ok=True)

# ログファイルのパス
log_path = log_dir.joinpath(log_file)

# ロギングの設定
# レベルはこの順で下にいくほど詳細になる
#   logging.CRITICAL
#   logging.ERROR
#   logging.WARNING --- 初期値はこのレベル
#   logging.INFO
#   logging.DEBUG
#
# ログの出力方法
# logger.debug('debugレベルのログメッセージ')
# logger.info('infoレベルのログメッセージ')
# logger.warning('warningレベルのログメッセージ')

# 独自にロガーを取得するか、もしくはルートロガーを設定する

# ルートロガーを設定する場合
# logging.basicConfig()

# 独自にロガーを取得する場合
logger = logging.getLogger(__name__)

# 参考
# ロガーに特定の名前を付けておけば、後からその名前でロガーを取得できる
# logging.getLogger("main.py").setLevel(logging.INFO)

# ログレベル設定
logger.setLevel(logging.INFO)

# フォーマット
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 標準出力へのハンドラ
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
stdout_handler.setLevel(logging.INFO)
logger.addHandler(stdout_handler)

# ログファイルのハンドラ
file_handler = logging.FileHandler(log_path, 'a+')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

#
# ここからスクリプト
#

if __name__ == '__main__':

    def main():

        DOMAIN = "PROD"
        CLIENT_ID = "iida@fujitsu.com"
        SERVICE_ID = "1ryq-e8n8-5g5n"

        DEVICE_NAME = "r1"
        COMMAND = "show ip int brief"

        with Client.create() as client:

            connect_data = client.oauth_connect_only(CLIENT_ID, domain=DOMAIN)

            ws = create_connection(str(connect_data.token_url))
            webbrowser.open(str(connect_data.sso_url))
            token = json.loads(ws.recv())['access_token']

            # print('Token:', token)

            # このトークンは1時間有効なので、保存しておいて再利用することもできる
            token_client = client.access_token_login(token, domain=DOMAIN)

            service = token_client.service(SERVICE_ID).wait()

            #print(service.status)
            #print(service.inventory)

            single_response = service.inventory[DEVICE_NAME].exec(COMMAND).wait()
            parsed_result = radkit_genie.parse(single_response)
            json_result = parsed_result[DEVICE_NAME][COMMAND].data
            print(json.dumps(json_result, indent=2))

        return 0

    # 実行
    sys.exit(main())

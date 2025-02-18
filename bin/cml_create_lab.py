#!/usr/bin/env python

#
# 標準ライブラリのインポート
#
import logging
import sys
from pathlib import Path

#
# 外部ライブラリのインポート
#
try:
    from virl2_client import ClientLibrary
    from virl2_client.models import Lab, Node
    from virl2_client.models.annotation import AnnotationText
except ImportError as e:
    logging.critical(str(e))
    sys.exit(-1)

#
# ローカルファイルからの読み込み
#
from cml_config import CML_ADDRESS, CML_USERNAME, CML_PASSWORD
from cml_config import LAB_TITLE


# このファイルへのPathオブジェクト
app_path = Path(__file__)

# このファイルの名前から拡張子を除いてプログラム名を得る
app_name = app_path.stem

# アプリケーションのホームディレクトリはこのファイルからみて一つ上
app_home = app_path.parent.joinpath('..').resolve()

# データ用ディレクトリ
data_dir = app_home.joinpath('data')

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

    def read_template_config() -> str:
        filename = 'cloud-init.yaml'
        p = app_home.joinpath(filename)
        try:
            with p.open() as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"{filename} not found")
            sys.exit(1)


    def create_ubuntu(lab: Lab, label: str, x: int = 0, y: int = 0) -> Node:
        # create_node(
        #   label: str,
        #   node_definition: str,
        #   x: int = 0, y: int = 0,
        #   wait: bool | None = None,
        #   populate_interfaces: bool = False, **kwargs
        # )→ Node

        node = lab.create_node(label, 'ubuntu', x, y)

        # 初期状態はインタフェースが存在しないので、追加する
        # Ubuntuのslot番号の範囲は0-7
        # slot番号はインタフェース名ではない
        # ens2-ens9が作られる
        for i in range(8):
            node.create_interface(i, wait=True)

        return node


    def create_text_annotation(lab: Lab, d: dict) -> AnnotationText:
        base_params = {
            'border_color': '#00000000',
            'border_style': '',
            'color': '#050505',
            'rotation': 0,
            'text_bold': False,
            'text_content': ' ',
            'text_font': 'monospace',
            'text_italic': False,
            'text_size': 12,
            'text_unit': 'pt',
            'thickness': 1,
            'x1': 0.0,
            'y1': 0.0,
            'z_index': 0
        }
        base_params.update(d)
        return lab.create_annotation('text', **base_params)



    def main():

        client = ClientLibrary(f"https://{CML_ADDRESS}/", CML_USERNAME, CML_PASSWORD, ssl_verify=False)

        # 接続を待機する
        client.is_system_ready(wait=True)

        # 同タイトルのラボを消す
        for lab in client.find_labs_by_title(LAB_TITLE):
            lab.stop()
            lab.wipe()
            lab.remove()

        # ラボを新規作成
        lab = client.create_lab(title=LAB_TITLE)

        #
        # ラボ定義ファイルの内容に沿って作成していく
        #

        # テキスト
        create_text_annotation(lab, {
            'color': '#050505',
            'text_content': 'インターネット',
            'x1': -247.0,
            'y1': -299.0,
            'z_index': 1
        })

        create_text_annotation(lab, {
            'color': '#808080FF',
            'text_content': 'Hyper-Vホスト \n 192.168.0.198',
            'x1': 59.0,
            'y1': -93.0,
            'z_index': 3
        })

        create_text_annotation(lab, {
            'color': '#808080FF',
            'text_content': '192.168.0.1',
            'x1': -160.0,
            'y1': -101.0,
            'z_index': 4
        })

        create_text_annotation(lab, {
            'color': '#808080FF',
            'text_content': 'RADKit接続 \n https://192.168.0.1:8081 \n (superadmin)',
            'x1': -7.0,
            'y1': -9.0,
            'z_index': 5
        })

        create_text_annotation(lab, {
            'color': '#808080FF',
            'text_content': '192.168.254.1/24',
            'x1': -196.0,
            'y1': -4.0,
            'z_index': 6
        })

        create_text_annotation(lab, {
            'color': '#808080FF',
            'text_content': '192.168.254.101',
            'x1': -187.0,
            'y1': 172.0,
            'z_index': 7
        })

        create_text_annotation(lab, {
            'color': '#808080FF',
            'text_content': 'radkit serial:5000\nR1 serial:5001',
            'x1': -480.0,
            'y1': -160.0,
            'z_index': 8
        })

        # 円
        lab.create_annotation(annotation_type='ellipse', **{
            'border_color': '#808080FF',
            'border_style': '',
            'color': '#A39FE9',
            'thickness': 1,
            'x1': -193.5,
            'y1': -272.5,
            'x2': 82.5,
            'y2': 68.5,
            'z_index': 0
        })

        # 四角形
        lab.create_annotation(annotation_type='rectangle', **{
            'border_color': '#808080FF',
            'border_radius': 0,
            'border_style': '',
            'color': '#BBFDBF',
            'thickness': 1,
            'x1': -11.0,
            'y1': -117.0,
            'x2': 211.0,
            'y2': 94.0,
            'z_index': 2
        })

        # 外部接続用のNATを作成する
        nat_node = lab.create_node("NAT", "external_connector", -200, -240)

        # 文字列"NAT"を設定することでNATとして動作する
        # 文字列"System Bridge"を設定するとブリッジになる
        nat_node.configuration = "NAT"

        # 母艦と通信するためのブリッジを作成する
        bridge_node = lab.create_node("bridge1", "external_connector", 0, -80)

        # 追加で作成した "bridge1" を指定する
        bridge_node.configuration = "bridge1"

        # Ubuntuを作る
        node_name = "radkit"
        ubuntu_node = create_ubuntu(lab, node_name, -200, -80)

        # タグを設定
        ubuntu_node.add_tag(tag="serial:5000")

        # ノードのconfigを設定する
        # Ubuntuに設定するcloud-init.yamlを取り出す
        template_config = read_template_config()
        ubuntu_node.config = template_config

        # ubuntuとNATを接続する
        lab.connect_two_nodes(ubuntu_node, nat_node)

        # ubuntuとbridge1を接続する
        lab.connect_two_nodes(ubuntu_node, bridge_node)

        # テスト用のノードと接続するアンマネージドスイッチを作る
        unmanaged_switch_node = lab.create_node("unmanaged-switch-0", "unmanaged_switch", -200, 80)

        # ubuntuとアンマネージドスイッチを接続する
        lab.connect_two_nodes(ubuntu_node, unmanaged_switch_node)

        # テスト用のCSR1000vを作成する
        csr1000v = lab.create_node("R1", "csr1000v", -200, 200)

        # タグを設定する
        csr1000v.add_tag("serial:5001")

        # CSR1000vとアンマネージドスイッチを接続する
        lab.connect_two_nodes(csr1000v, unmanaged_switch_node)

        # start the lab
        # lab.start()

        # print nodes and interfaces states:
        for ubuntu_node in lab.nodes():
            print(ubuntu_node, ubuntu_node.state, ubuntu_node.cpu_usage)
            for interface in ubuntu_node.interfaces():
                print(interface, interface.readpackets, interface.writepackets)


        return 0

    # 実行
    sys.exit(main())

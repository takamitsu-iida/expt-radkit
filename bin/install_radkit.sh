#!/bin/bash

# 実行方法
# curl -sf https://raw.githubusercontent.com/takamitsu-iida/expt-radkit/refs/heads/main/bin/install_radkit.sh | /bin/bash -s

RADKIT_VERSION="1.7.6"

SCRIPT_FILENAME="cisco_radkit_${RADKIT_VERSION}_linux_x86_64.sh"

SCRIPT_PATH="http://192.168.0.198/${SCRIPT_FILENAME}"


if [ ! -e /tmp/${SCRIPT_FILENAME} ]; then
    # /tmpにまだファイルがなければダウンロードする
    echo "download RADKit install script to /tmp"

    # wgetでファイルを取得して/tmpに保存する
    wget -P /tmp ${SCRIPT_PATH}

    if [ ! -e /tmp/${SCRIPT_FILENAME} ]; then
        echo "download failed"
        exit 1
    fi
fi

# 実行する
/bin/sh /tmp/${SCRIPT_FILENAME} -- --accept-all --systemd

# ポストインストールを実行する
/bin/sh /opt/radkit/versions/${RADKIT_VERSION}/post-install.sh

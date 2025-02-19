#!/bin/bash

# 実行方法
# curl -sf https://raw.githubusercontent.com/takamitsu-iida/expt-radkit/refs/heads/main/bin/install_radkit.sh | /bin/bash -s

SCRIPT_FILENAME=cisco_radkit_1.7.6_linux_x86_64.sh

SCRIPT_PATH=http://192.168.122.198/${SCRIPT_FILENAME}

echo "download RADKit install script to /tmp"
wget -P /tmp ${SCRIPT_PATH}

if [ -e /tmp/${SCRIPT_FILENAME} ]; then
  echo "download failed"
  exit 1
fi

# sh /tmp/cisco_radkit_1.7.4_linux_x86_64.sh
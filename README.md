# RADKitをCMLで使うメモ

<br>

## CML環境

Hyper-Vを有効にしたWindows11上でCMLを動かしています。

CMLラボ内の仮想Ubuntuサーバからwgetでファイルを落とせるように、どこかに自分で制御できるHTTPサーバを立てておきます。
ここでは母艦になっているWindows11でIISを有効にしておきます。

<br>

## RADKitをダウンロード

母艦になっているWindows11で以下のサイトを開きます。

https://radkit.cisco.com/

画面右上のDownloadsからインストーラのシェルスクリプトをダウンロードします。

> [!NOTE]
>
> 2024年11月時点での最新
>
> cisco_radkit_1.7.4_linux_x86_64.sh
>
> をダウンロードしました。

これをIISのルートにコピーしておきます。

<br>

## CMLのラボに仮想マシンを作成する

Ubuntuとdesktopマシンを作成します。

UbuntuはRADKitをインストールするマシン、desktopマシンはRADKitの設定をブラウザで行うためのマシンです。

Ubuntuはインタフェースを追加して2本足にします。

- ens2はNATで外に出ていく通信に使うインタフェース（dhcp）
- ens4はラボ内のネットワーク機器と接続するインタフェース(192.168.254.254/24)

UbuntuのTagsには `serial:50000` と設定して5000番ポートでシリアルコンソール接続できるようにします。

Ubuntuに以下のYAMLをCONFIGにコピペします。

```yaml
#cloud-config
hostname: radkit
manage_etc_hosts: True
system_info:
  default_user:
    name: root
password: cisco
chpasswd: { expire: False }
ssh_pwauth: True
ssh_authorized_keys:
  - your-ssh-pubkey-line-goes-here
timezone: Asia/Tokyo
locale: ja_JP.utf8
write_files:
  - path: /etc/netplan/50-cloud-init.yaml
    content: |
      network:
        ethernets:
          ens2:
            dhcp4: true
            #nameservers:
            #  addresses:
            #    - 192.168.122.1

          ens3:
            dhcp4: false
            addresses:
              - 192.168.254.254/24
            #gateway4: 192.168.254.1
            routes:
              - to: 10.0.0.0/8
                via: 192.168.254.1

        version: 2

runcmd:
  - sudo netplan apply

  - sudo ufw allow 8081/tcp

  - sudo ufw allow 8181/tcp

  - |
    sudo cat - << 'EOS' >> /root/.bashrc
    rsz () if [[ -t 0 ]]; then local escape r c prompt=$(printf '\e7\e[r\e[999;999H\e[6n\e8'); IFS='[;' read -sd R -p j"$prompt" escape r c; stty cols $c rows $r; fi
    rsz
    EOS

  - |
    sudo cat - << 'EOS' >> /root/.bashrc
    RADKIT_ROOT="/opt/radkit/bin"
    export PATH=$RADKIT_ROOT:$PATH
    EOS

  # - wget -P /tmp 192.168.122.198/cisco_radkit_1.7.4_linux_x86_64.sh

```

desktopマシンはインタフェースを追加します。

desktopマシンのeth1とUbuntuを接続します。

以下のシェルスクリプトをCONFIGに流し込んで、ホスト名とログインユーザを設定します。

```bash
# this is a shell script which will be sourced at boot
hostname desktop

# configurable user account
USERNAME=cisco
PASSWORD=cisco

# configure networking
# ifconfig eth1 192.168.0.1 netmask 255.255.255.0 up
# route add -net 10.0.0.0/8 dev eth1
```

<br>

> [!NOTE]
>
> 以下の作業はすべてrootユーザで実行することを前提にしています。

<br>

TeraTERMを起動してポート5000番にtelnetして、Ubuntuのシリアルコンソールに接続します。

rootでログインします。

<br>

## RADKitをインストールする

wgetでインストーラをダウンロードします。

ここでは母艦のWindows11（192.168.122.198）のIISのサーバルートに置いたファイルをダウンロードしています。

```bash
wget -P /tmp 192.168.122.198/cisco_radkit_1.7.4_linux_x86_64.sh
```

インストールします。

```bash
sh /tmp/cisco_radkit_1.7.4_linux_x86_64.sh
```

システムにインストールするか、ユーザ個別にインストールするか聞かれるので、`system` を選びます。

インストール後に以下のような注意喚起のメッセージが表示されます。

```bash

lq POST-INSTALLATION INSTRUCTIONS qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk
x #!/bin/bash                                                             x
x                                                                         x
x # Firewall                                                              x
x # `ufw` detected.                                                       x
x # IF you are using it, please consider these suggested rules:           x
x # - the following port must be opened for WebUI access (recommended)    x
x sudo ufw allow 8081/tcp                                                 x
x # - the following port must be opened for Direct Connect (optional)     x
x sudo ufw allow 8181/tcp                                                 x
x                                                                         x
x                                                                         x
x # Start or restart RADKit service                                       x
x # RADKit is not running.                                                x
x # To start RADKit service, use the following command:                   x
x sudo systemctl start radkit                                             x
x                                                                         x
x                                                                         x
x # Bootstrap RADKit Service using the WebUI:   https://localhost:8081    x
x # or RADKit Control:   /opt/radkit/bin/radkit-control system bootstrap  x
x # (for non-interactive bootstrap, please refer to the documentation)    x
x                                                                         x
x # Enroll and configure RADKit Service using the WebUI or RADKit Control x
x # (for detailed instructions, please refer to the documentation)        x
x                                                                         x
mqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj


lq WARNING qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk
x Post installation instructions have been written into                        x
x /opt/radkit/versions/1.7.4/post-install.sh.                                  x
x Please adjust the script to your site policies and run when ready using the  x
x command: sh /opt/radkit/versions/1.7.4/post-install.sh                       x
mqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj


lq WARNING qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk
x Make sure that /opt/radkit/bin is in your PATH.         x
x To uninstall, run: /opt/radkit/versions/1.7.4/uninstall x
mqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj

```

これら注意喚起メッセージに素直に従うなら、次のスクリプトを実行します。

```bash
sh /opt/radkit/versions/1.7.4/post-install.sh
```

サービスの起動状況を確認します。

```bash
systemctl status radkit
```

こんな感じでactiveになっていればOKです。

```bash
root@radkit:~# systemctl status radkit
● radkit.service - RADKit Service
     Loaded: loaded (/etc/systemd/system/radkit.service; enabled; vendor preset>
     Active: active (running) since Sun 2024-11-10 12:07:04 JST; 10min ago
   Main PID: 576 (radkit-service)
      Tasks: 8 (limit: 2310)
     Memory: 293.2M
        CPU: 3.084s
     CGroup: /system.slice/radkit.service
             mq576 /opt/radkit/versions/1.7.4/python/bin/python3 /opt/radkit/bi>
```

Ubuntuに割りあてられているIPアドレスを確認します。

```bash
ip address
```

実行例。下記の例ではens2に192.168.255.167が割り当てられています。

このアドレスをメモしておきます。

```bash
root@radkit:~# ip a
2: ens2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:06:59:b3 brd ff:ff:ff:ff:ff:ff
    altname enp0s2
    inet 192.168.255.167/24 metric 100 brd 192.168.255.255 scope global dynamic ens2
       valid_lft 2315sec preferred_lft 2315sec
    inet6 fe80::5054:ff:fe06:59b3/64 scope link
       valid_lft forever preferred_lft forever
```

操作する端末をdesktopに切り替えます。

desktopマシンのアイコンを右クリックしてVncを選択します。

左上の Applications → Settings → keyboard を選択します。

Layoutタブを選択。

Use system defaultsのトグルスイッチをオフに変更。

+Addで Japanese → Japanese(Kana 86)を選択します。

English(US)を -Remove します。

Firefoxを起動して、

`https://ubuntuのIPアドレス:8081`

にアクセスします。

Warning: Potential Security Risk Aheadと表示されますが、Advancedを選択して先に進みます。

`Register superadmin user` 画面が表示されますので、superadminのパスワードを設定します。

Service Identity Certificate の部分にある 「Enroll with SSO」 を選択してサービスを有効にします。

CCOに登録してあるメールアドレスを入力します。

表示されるリンクをクリックして、Ciscoの認証ページでログインします。

下のページに戻ってみると、重要な情報が画面の上の部分に表示されますので、それをメモします。

```bash
Domain: PROD Service ID: 81pr-id0q-y4kt
```

左側のDevicesから装置の情報を登録します。

<BR>

### クライアントをインストール

WSLに入れます。

```bash
sh cisco_radkit_1.7.4_linux_x86_64.sh
```

customを選択します。

~/.bashrcに以下を追加してPATHを通します。

```bash
## RADKit
RADKIT_ROOT="$HOME/.local/radkit"
export PATH="$RADKIT_ROOT/bin:$PATH"
```


```bash
radkit-client
```

```bash
sso_login("iida@fujitsu.com)
```

リンクが表示されるので、それをクリックします。

<BR>

ラボ機器へのログインは次のようにします。

```bash
$ radkit-interactive --domain PROD --service-sn r7ih-z54p-5297 --sso-email iida@fujitsu.com --device csr1000v-1
```

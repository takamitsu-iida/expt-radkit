# RADKitをCMLで使うメモ

<br>

## CML環境

Hyper-Vを有効にしたWindows11上でCMLを動かしています。

このWindows11には物理NICが5個あり、そのうちの2個をCMLとブリッジしています。★ここ重要

一つは実際にインターネットに出ていけるLAN、もう一つのNICはリンクアップしているだけの何もつながっていないNICです。

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

Ubuntuを作成します。

UbuntuはRADKitをインストールするマシンです。

インターネット上のクラウドと通信しますので外部接続が必要です。これはNAT接続を利用します。

RADKitの設定はブラウザを使ったGUI操作になりますので、Ubuntuに対してブラウザで接続できなければいけません。
その経路としてもう一つのNICを使い、母艦になっているWindows11からブラウザでアクセスできるようにします。
母艦のWindows11はこのNICに対して192.168.0.198/24のアドレスを固定で設定していますので、
RADKitのUbuntuには192.168.0.1/24のアドレスを採番します。

RADKitは同時にCMLのラボ機器とも接続します。それ用のLANも必要ですので、合計3本足のマシンになります。

- ens2はNATで外に出ていく通信に使うインタフェース（dhcp）
- ens3は母艦のWindows11とブリッジで接続するインタフェース（192.168.0.1/24）
- ens4はラボ内のネットワーク機器と接続するインタフェース(192.168.254.1/24)

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
              - 192.168.0.1/24
            #gateway4: 192.168.254.1

          ens4:
            dhcp4: false
            addresses:
              - 192.168.254.1/24
            #routes:
            #  - to: 10.0.0.0/8
            #    via: 192.168.254.101

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

これら注意喚起メッセージに素直に従って、次のスクリプトを実行します。

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
root@radkit:~# ip address
2: ens2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:19:eb:e6 brd ff:ff:ff:ff:ff:ff
    altname enp0s2
    inet 192.168.255.114/24 metric 100 brd 192.168.255.255 scope global dynamic ens2
       valid_lft 3418sec preferred_lft 3418sec
    inet6 fe80::5054:ff:fe19:ebe6/64 scope link
       valid_lft forever preferred_lft forever
3: ens3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:02:14:24 brd ff:ff:ff:ff:ff:ff
    altname enp0s3
    inet 192.168.0.1/24 brd 192.168.0.255 scope global ens3
       valid_lft forever preferred_lft forever
    inet6 fe80::5054:ff:fe02:1424/64 scope link
       valid_lft forever preferred_lft forever
4: ens4: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:00:0f:11 brd ff:ff:ff:ff:ff:ff
    altname enp0s4
    inet 192.168.254.1/24 brd 192.168.254.255 scope global ens4
       valid_lft forever preferred_lft forever
    inet6 fe80::5054:ff:fe00:f11/64 scope link
       valid_lft forever preferred_lft forever
```

ens2の192.168.255.114/24はNATで外部に接続するためのアドレスです。

ens3の192.168.0.1/24は固定で設定したものです。このLAN上には母艦のWindows11しか存在しません。

ens4の192.168.254.1/24は固定で設定したもので、ラボ内の機器と接続するためのアドレスです。

RADKitはCiscoのクラウドと通信しますので、インターネットとの接続性を確認します。

```bash
root@radkit:~# ping www.google.co.jp
PING www.google.co.jp (172.217.26.227) 56(84) bytes of data.
64 bytes from bom05s09-in-f3.1e100.net (172.217.26.227): icmp_seq=1 ttl=118 time=6.65 ms
64 bytes from nrt12s51-in-f3.1e100.net (172.217.26.227): icmp_seq=2 ttl=118 time=7.15 ms
64 bytes from bom05s09-in-f3.1e100.net (172.217.26.227): icmp_seq=3 ttl=118 time=9.23 ms
64 bytes from nrt12s51-in-f3.1e100.net (172.217.26.227): icmp_seq=4 ttl=118 time=7.35 ms
64 bytes from nrt12s51-in-f3.1e100.net (172.217.26.227): icmp_seq=5 ttl=118 time=8.24 ms
64 bytes from bom05s09-in-f3.1e100.net (172.217.26.227): icmp_seq=6 ttl=118 time=8.06 ms
^C
--- www.google.co.jp ping statistics ---
6 packets transmitted, 6 received, 0% packet loss, time 5008ms
rtt min/avg/max/mdev = 6.650/7.781/9.232/0.842 ms
```

<BR>

> RADKit serviceが接続する宛先はここですが、pingには応答しません。
>
> wss://prod.radkit-cloud.cisco.com/forwarder-1/

<BR>

外部接続が問題なければ、母艦のWindows11のブラウザからRADKitのURL `https://192.168.0.1:8081` に接続します。

初めて接続すると superadmin user のパスワードを設定せよ、と言われますので設定します。

パスワードを設定したら、最初にクラウドと接続してサービスIDを取得します。

画面内の「Enroll with SSO」をクリックします。

CCOに登録したメールアドレスを入力します。

`Follow the SSO login link to continue: [CLICK HERE]` をクリックすると認証が走ります。

Acceptを押します。

もとのページに戻ると、画面の上部に重要な情報が表示されていますので、それをコピペしてどこかに保存しておきます。

> 例： Domain: PROD Service ID: 1ryq-e8n8-5g5n


画面左側のRemote Usersから接続許可を払い出すユーザを登録します。最初は自分を登録しておけばいいでしょう。

画面左側のDevicesから装置の情報を登録します。

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

domainとservice-snは先程コピペしておいた情報です。

```bash
$ radkit-interactive --domain PROD --service-sn 1ryq-e8n8-5g5n --sso-email iida@fujitsu.com --device r1
```

<br>

### クライアントを削除

インストールしたときに、削除方法が表示されています。

```bash
┌─ WARNING ────────────────────────────────────────────────────────────┐
│ Make sure that /home/iida/.local/radkit/bin is in your PATH.         │
│ To uninstall, run: /home/iida/.local/radkit/versions/1.7.4/uninstall │
└──────────────────────────────────────────────────────────────────────┘
```

---
layout: post
title: Supervisordの使い方
date: '2018-7-04T00:00:00.000+09:00'
author: s sato
tags:
- linux
---

### Supervisordとは？

Supervisordは`systemctl`や`/etc/init.d`みたいなデーモンプロセスを管理するデーモンプロセス  
プロセス管理するだけなら、それらを使えばよいが、Supervisordはプロセスが不測の事態で停止した際に、自動で再起動が可能という利点がある。  
基本的にサーバープロセスは、不測の事態で終了するようなことがないように、すべての例外をキャッチするように作っておくべきだが、どうしても
人間が作る以上、ミスがある可能性がある。  
また、OOM Killerに殺されるのは、プログラム上どう作っても防ぐことができない。  
万一メモリリークしていた時でも、プロセスが死んだあと、即座に起動してくれるSupervisordを使っていれば何とかなるかもしれない。  
なので、停止が許されないサーバーの起動は、`systemctl`よりもSupervisordをつかうべきな気がする。  

(あと、webコンソールがあるし、プロセスの定義も`systemctl`より簡潔)


### インストール

```
sudo yum install supervisor -y
```


### 設定

`/etc/supervisord.conf`に以下の内容を記載  

```
[program:my-server]
command=/usr/local/bin/my-server
autostart=true
autorestart=true
```

`/usr/local/bin/my-server`は、サーバーの起動コマンドだが以下の点に注意   
- ファイルの実行権限(+x)があること
- `#!/usr/bin/sh`のように実行するプログラムが明示されていること



### Supervisordを自動起動する

Supervisordで各種のプロセスを自動起動するには、Supervisord自体がサーバーの起動時に、起動していなければならない。  
これには、systemctlをどうしても使う必要がある。  

```
systemctl enable supervisord
systemctl start supervisord
```


`supervisorctl status` で自分の定義したプロセスが見えればOK

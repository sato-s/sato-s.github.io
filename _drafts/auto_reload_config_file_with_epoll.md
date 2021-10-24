---
layout: post
title: fsnotifyを使って自動で再読み込みされる設定ファイルを作る
date: '2021-08-01T00:17:00.000+09:00'
author: s sato
tags:
- go
- linux
---

大抵のサーバープログラムはなんらんかの設定ファイルをもっている。
PostgreSQLでいうとpostgresql.confやpg_hba.conf、nginxでいうとnginx.confがある。  
これらのプログラムはシグナルをつかって設定ファイルをサーバープロセスの再起動なしで反映するための仕組みを用意してくれていて、
いずれもSIGHUPをメインのプロセスに送ることで設定ファイルを再度読み込んでくれる。
例えば、postgresqlなら`pg_ctl reload`で、nginxなら`nginx -s reload`コマンドでシグナルを送ると設定ファイルを再度読み込んでくれる。
これによってサーバーのダウンタイムなしでパラメーターを変更することができる。  

一方でRails(developmentモード)やwebpack-dev-serverの場合、ファイルを変更するとそれだけで
設定を反映してくれる。(これは設定ファイルというよりもソースコードそのものの変更を自動で検出して反映してくれる)  
Railsやwebpack-dev-serverの場合、ダウンタイムを防ぐのではなく開発中の確認作業を便利にするために、シグナルを明に受けなくても
設定が反映されるようになっている。  

このように設定を勝手に反映してくれるのは、意図せぬ変更が発生する可能性があるので、プロダクション環境のサーバーには不向きだが、
個人的に使うような場合にはとても便利だ。  
Goで個人的に使うサーバープロセスを立てたかったので、これを試してみた。


## inotifyとfsnotify

ファイルの変更の監視は、もちろんポーリングすることでもできるが、あまり効率的ではない。
Linuxの場合[inotify](https://linuxjm.osdn.jp/html/LDP_man-pages/man7/inotify.7.html)
で取得したファイルディスクリプタを
[epoll](https://linuxjm.osdn.jp/html/LDP_man-pages/man7/epoll.7.html)
などで監視することによって、
OS側からファイルへの変更があった場合に通知してもらうことができる。  
これらのシステムコールを直接使って監視を行うこともできるが、
Goでは[fsnotify](https://github.com/fsnotify/fsnotify)
というライブラリがあり、うまくラップしてくれている。
しかも、Linux以外のOSでも別のシステムコールを使うことで動作してくれる。

## fsnotifyの使い方

基本的な使い方としては以下のような形になる

```go
package main

import (
	"github.com/fsnotify/fsnotify"
	"log"
)

func main() {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		panic(err)
	}
  // sample_fileを監視
	if err := watcher.Add("sample_file"); err != nil {
		panic(err)
	}

	for {
		select {
		case event := <-watcher.Events:
			log.Printf("EVENT: %+v\n", event.Op)
		}
	}
}

```

上を動作させた状態で`sample_file`に対して以下の操作を行ってみよう。


```shell
$ echo "test" >> sample_file
$ touch sample_file
$ rm sample_file
```

そうすると各操作が行われるごとに、以下のようにイベントの種類を出力してくれる。

```
2021/10/24 15:49:33 EVENT: WRITE
2021/10/24 15:49:39 EVENT: CHMOD
2021/10/24 15:49:56 EVENT: REMOVE
```

## Goにおける設定ファイル

サーバープロセスの設定ファイルとしては以下のようなYamlに値を書いていくことにしたい。

```yaml
a: 1
b: "test"
```

このようなYamlをGoの内部で使用しようとする場合、以下のような感じでYamlをstructにマッピング
してから使用するケースがほとんどだと思う。

```go
import (
	"fmt"
	"gopkg.in/yaml.v2"
	"io/ioutil"
)

type Config struct {
	A int
	B string
}

func NewConfig(filename string) (*Config, error) {
	c := &Config{}
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		return nil, err
	}
	if err := yaml.Unmarshal([]byte(data), &c); err != nil {
		return nil, err
	}

	return c, nil
}

func main() {
	config, err := NewConfig("config.yaml")
	if err != nil {
		panic(err)
	}
	fmt.Printf("%+v", config)
}
```

上のような`Config`型が最初に与えられたファイル(上の場合は`config.yaml`)に変更が
ある場合に自動で変更されるようにしてみる。


## fsnotifyによるyamlの再読み込み



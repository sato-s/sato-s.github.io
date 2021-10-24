---
layout: post
title: fsnotifyを使って自動で再読み込みされる設定ファイルを作る
date: '2021-10-23T00:17:00.000+09:00'
author: s sato
tags:
- go
- linux
---

大抵のサーバープログラムはなんらんかの設定ファイルをもっている。
PostgreSQLでいうとpostgresql.confやpg_hba.conf、nginxでいうとnginx.confがある。  
これらにはシグナルをつかって設定ファイルをサーバープロセスの再起動なしで反映するための仕組みがある。  
例えば、postgresqlなら`pg_ctl reload`で、nginxなら`nginx -s reload`コマンドを実行すると
SIGHUPがメインのプロセスに送られ、サーバーの設定を再度読み込んでくれる。
これによってサーバーのダウンタイムなしで
`work_mem`(SQLのソート等に利用可能なメモリの量)などの値を
変更することができる。  

一方でRails(developmentモード)やwebpack-dev-serverの場合、ファイルを変更するとそれだけで
設定を反映してくれる。(これは設定ファイルというよりもソースコードそのものの変更)  
Railsやwebpack-dev-serverの場合、開発中の確認作業を便利にするために、シグナルを明に受けなくても
設定が反映されるようになっているのだろう。  

このようにファイルが変わっただけで設定を勝手に反映してくれるのは、意図せぬ変更が発生する可能性があるので、プロダクション環境のサーバーには不向きだが、
個人的に使うような場合にはとても便利だ。  
Goで個人的に使うサーバープロセスを立てたかったので、これを試してみた。


## inotifyとfsnotify

ファイルの中身を定期的ポーリングし
変更を検知することもできるが、このような方法は
あまり効率的ではない。
できれば、ファイルへの変更があった場合にのみ設定ファイルを再度読み込む
ようなサーバープロセスにしたい。  
Linuxの場合[inotify](https://linuxjm.osdn.jp/html/LDP_man-pages/man7/inotify.7.html)
で取得したファイルディスクリプタを
[epoll](https://linuxjm.osdn.jp/html/LDP_man-pages/man7/epoll.7.html)
などで監視することによって、
OS側からファイルへの変更があった場合に通知してもらうことができる。  

これらのシステムコールを直接使って監視を行うこともできるが、
Goでは[fsnotify](https://github.com/fsnotify/fsnotify)
というライブラリがあり、うまくラップしてくれている。
しかもLinux以外のOSも別のシステムコールを使うことでサポートしてくれている。

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

// Yamlから設定内容を読み込みConfigを返却する
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
```

上のような`Config`型は以下のように使用することでYamlないの設定内容を読みだすことができる。

```go
func main() {
	config, err := NewConfig("config.yaml")
	if err != nil {
		panic(err)
	}
	fmt.Printf("%d", config.A) // => 1
	fmt.Printf("%s", config.B) // => "test"
}

```

上のような`Config`型が最初に与えられたファイル(上の場合は`config.yaml`)への変更を
自動で検知し変更内容が反映されるようにしてみる。


## 変更の自動検知と反映

`Config`型の自動更新を行う場合には、fsnotifyによってファイルの変更を検知した際に
ファイルを再度読み込んで、それを`Config`型の属性に再度反映させてやるという操作が必要になる。
再度のyamlの読み込みに備えてファイル名を記憶しておく必要があるのでstructのprivateな属性として`filename`
を用意しておく

```go
type Config struct {
	A        int
	B        string
	filename string
}
```

また、元のコードからYamlの読み出しと構造体へのマッピングを行っている箇所を`loadFile`
として切り出しておく。
こうすることで`Config`型を初期化するときだけでなく後にfsnofityで変更を検知した際にも
同じ`loadFile`を呼び出すことで変更を検知することができる。

```go
func (c *Config) loadFile() error {
	data, err := ioutil.ReadFile(c.filename)
	if err != nil {
		return err
	}
	err = yaml.Unmarshal([]byte(data), &c)
	return err
}
```

fsnotifyによる変更の検知はchannelを使って行うことができる。
この変更の検知を行うメソッド`run`を以下のように定義する。

```go
func (c *Config) run() error {
	watcher, err := fsnotify.NewWatcher()
	defer watcher.Close()
	if err != nil {
		return err
	}
	if err := watcher.Add(c.filename); err != nil {
		return err
	}

	for {
		select {
		case event := <-watcher.Events:
			if event.Op&fsnotify.Write == fsnotify.Write {
				// 書き込み(fsnotify.Write)があるとここを通る
				err := c.loadFile() // 設定の読み出し
				if err != nil {
					log.Printf("Error: %s", err)
				} else {
					log.Printf("Refreshed setting from %s", c.filename)
				}
			}
		case err := <-watcher.Errors:
			log.Printf("Error: %s", err)
		}
	}
	return nil
}
```

あとは`NewConfig`内で`run`をgoroutineで呼び出すようにしておけば、
`run`内の`for`ループが走り続けるので、自動更新が行われる。

```go
func NewConfig(filename string) (*Config, error) {
	config := &Config{filename: filename}

	if err := config.loadFile(); err != nil {
		return nil, err
	}
	// runをgoroutineで呼び出し
	go config.run()
	return config, nil
}
```

最終的なソースは[これ](https://github.com/sato-s/fsnotify_config/blob/master/main.go)


## 使い方

変更の自動検知と反映を行う前と同様に
`config, err := NewConfig("config.yaml")`
のように変数に代入して使用する。
`config.A`や`config.B`のような形式で属性にアクセスすると
その時にYamlに記載されている最新の値を読みだすことができる。  
ただし、このままだと設定の読み書きと、自動検知時の属性の更新の間で競合が発生する可能性
があるので、きちんとしたものを作る際にはmutexなどでアクセスのされ方を制御す必要がある。



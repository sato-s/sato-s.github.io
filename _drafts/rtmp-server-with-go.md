---
layout: post
title: GoでRTMPサーバー
date: '2018-12-26T00:17:00.000+09:00'
author: s sato
tags:
- Go
- rtmp
- ffmpeg
---


> Real Time Messaging Protocol (RTMP) とは、Adobe が開発している、Adobe Flash プレーヤーとサーバーの間で、音声・動画・データをやりとりするストリーミングのプロトコル。元々は Macromedia が開発していて、Adobe に買収された。プロトコルの仕様は公開されている[1]。

*wikipediaより*  

RTMPの動画を再生するには、基本的にFlash Playerがひつようになる。Flash Playerを使うようなことは、いまからさすがにないだろう。  
Flashの終了やHLSの登場に伴い、RTMPは徐々に廃れつつあるらしい。  
が、それはあくまでPlayer側の話。  
Youtube LiveやFacebook Live、Twitchなどのライブ配信サービスでは、依然として配信データをRTMPで受け付けているし、
その影響で[OBS](https://obsproject.com/)や[DJI Go](https://play.google.com/store/apps/details?id=dji.go.v4&hl=en)などのライブ配信クライアントも、RTMPでの送信がデフォルト。  
(Youtubeとかは、RTMPで受け付けた動画を別のプロトコルに変換してから配信している。)  
なので、RTMPサーバーをGoで立ててみた。  

## ffmpegの使い方

デバックのために[ffmpeg](https://www.ffmpeg.org/)を使用する。  
初めて使ったが、動画用のImagemagickみたいなものだと思う、たぶん。  
いくつかの使い方を紹介しておく。  


### 動画のメタデータの表示

`ffmpeg`は`-i`オプションで入力動画を指定できる

```
$ ffmpeg -i test.mov
 # 略
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'test.mov':
  Metadata:
    major_brand     : qt
    minor_version   : 512
    compatible_brands: qt
    encoder         : Lavf58.25.100
    comment         : DE=None, Mode=P, DSW=0001
    location        : +35.309178+139.531178+7.100
    location-{    : +35.309171+139.538178+7.100
  Duration: 00:00:15.02, start: 0.000000, bitrate: 59628 kb/s
    Stream #0:0(eng): Video: h264 (High) (avc1 / 0x31637661), yuv420p(tv, bt709), 1920x1080 [SAR 1:1 DAR 16:9], 59626 kb/s, 23.98 fps, 23.98 tbr, 24k tbn, 47.95 tbc (default)
    Metadata:
      handler_name    : DataHandler
      encoder         : AVC encoder
At least one output file must be specified
```

### フォーマットの変換

フォーマットの変換がかなり簡単。  
いくつか試したが、知ってるフォーマットはほとんど何とかしてくれる。  

```
ffmpeg -i test.mov test.mpeg
ffmpeg -i test.mov test.avi
ffmpeg -i test.mov test.flv
```

### 動画の切り出し

`-ss`で切り出しの開始時刻を指定し、`-t`で何秒間切り出すのかを指定する。  

```
ffmpeg -i test.mov -ss 00:00:03 -t 10 test_short.mov
```

### 動画のRTMPサーバーへの配信

引数にURLをとるとそこに動画を送信してくれる。  
`-f flv`で動画をflvに変換して送信している。`-re`オプションで元動画の経過時間を元に配信タイミングを決めてくれる。  
(これがないとすぐに配信が終わってしまう。)   

```
ffmpeg -re -i test.mov -c copy -f flv rtmp://********/*****
```

## RTMPサーバーを立てる

Nginxでも拡張モジュールRTMPサーバーが立てられるが、かなり細かな制御がしたかったので、[joy4](https://github.com/nareix/joy4/)というのを使ってみた。  
[example](https://github.com/nareix/joy4/tree/master/examples)にいろいろな例が載っているが、最小限のRTMPサーバーは以下でできる。  

```
package main

import (
  "github.com/nareix/joy4/av/avutil"
  "github.com/nareix/joy4/av/pubsub"
  "github.com/nareix/joy4/format"
  "github.com/nareix/joy4/format/rtmp"
)

var queue *pubsub.Queue

func init() {
  format.RegisterAll()
  queue = pubsub.NewQueue()
}

func main() {
  server := &rtmp.Server{}

  server.HandlePlay = func(conn *rtmp.Conn) {
    avutil.CopyFile(conn, queue.Latest())
  }

  server.HandlePublish = func(conn *rtmp.Conn) {
    avutil.CopyFile(queue, conn)
  }

  server.ListenAndServe()
}
```

`HandlePlay`が再生時のコールバックで、`HandlePubish`が受信時のコールバック  
受信した動画をキューにコピーして、再生の要求が来た時に、キューの中身を再生要求のコネクションに流すようになっている。  


送信(動画はH264で圧縮されている必要がある。)  

```
ffmpeg -i sample.mp4 -c copy -f flv rtmp://localhost/
```

受信(プレイヤーが立ち上がって、中身が見えるはず)  

```
ffplay rtmp://localhost/
```

## タイトル動画

せっかくなので、Nginxだと(たぶん)できなさそうなことをしてみる。  
ライブ配信の再生要求が来た際に、特定の動画を流してみる。  

```
func main() {
  server := &rtmp.Server{}

  server.HandlePlay = func(conn *rtmp.Conn) {
    f, _ := os.Open("title.mp4")
    defer f.Close()
    title := mp4.NewDemuxer(f)
    avutil.CopyFile(conn, title)
    avutil.CopyFile(conn, queue.Latest())
  }

  server.HandlePublish = func(conn *rtmp.Conn) {
    avutil.CopyFile(queue, conn)
  }

  server.ListenAndServe()
}
```

上のように、先ほどのコードの`HandlePlay`で`queue`の中身よりも先に、特定の動画の中身を再生要求コネクションに渡す。  



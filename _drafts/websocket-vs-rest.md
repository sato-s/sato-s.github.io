---
layout: post
title: WebSocketとRESTは併用すべきか？
date: '2023-05-13T12:38:00.000+09:00'
author: s sato
tags:
- その他
---

チャットや複数人でのお絵描きアプリでは、リアルタイムな通信のためWebSocketが使用される。
チャットのメッセージや描いた図形の情報など双方向に素早くやり取りする必要のある情報に関しては、明らかにWebSocketを使って通信するのが良い。
しかし、チャットアプリやお絵描きアプリは、リアルタイムの通信を必要とするもののほかにも、チャットルームの作成、ユーザー情報の変更、アバター画像のアップロードなど、リアルタイムである必要が全くないものも存在する。
このような情報はWebSocketを別に使う必要はなく、RESTでも十分ではある。
一般的にリアルタイムな通信を必要とするアプリケーションで、このような情報をRESTで扱うのかわからなかったので調査した。

## Tinodeの場合

[Tinode](https://github.com/tinode/chat)はオープンソースのインスントメッセージングアプリ。  
![]({{ site.url }}/assets/websocket-vs-rest/tinode-sample.png)

ソースコードを見ればどの通信にREST or WebSocketを使っているかわかるかと思って、オープンソースのものを調査したが、よく考えたらブラウザの開発者コンソールから通信を見るの簡単だった。  
NetworkタブをWSで絞ると、websocketでの通信があるとメッセージを表示してくれる
![]({{ site.url }}/assets/websocket-vs-rest/chrome-dev.png)


メッセージの送信時はもちろんWebSocketを使用していた。

**メッセージの送信 -> WebSocket**
```
{"pub":{"id":"****","topic":"grp******","noecho":true,"content":"sample"}}
```

以下のようなRESTでも問題なさそうな通信に関してもWebSocketだった。

**ログイン -> WebSocket**
```
{"login":{"id":"****","scheme":"basic","secret":"**********"}}
```

**グループの作成 -> WebSocket**
```
{"sub":{"id":"****","topic":"new102180","set":{"desc":{"public":{"fn":"サンプル","note":"ディスクリプション","photo":{"data":"␡","ref":"/v0/file/s/yz3lDwrCX6c.png","type":"jpeg"}},"private":{"comment":"コメント"}}},"get":{"data":{"limit":24},"what":"data sub desc"}}}
```

上のグループの作成の際は、下のようにグループのイメージ画像を指定していたが、こちらもWebSocketで画像の更新を伝えてた。

![]({{ site.url }}/assets/websocket-vs-rest/tinnode-create-group.png)

ただ、画像ファイル本体は流石にWebSocketを使用しておらず、以下のURLに対するmultipartのPOSTで画像をアップロードしていた。

`https://web.tinode.co/v0/file/u/`


## Cuckooの場合

[Cuckoo](https://cuckoo.team/test-session)は複数人が同時に使えるタイマーアプリ

![]({{ site.url }}/assets/websocket-vs-rest/cuc-timer.png)


**ユーザー名の登録 -> WebSocket**

```
42/test-session,["update user","username"]
```

**タイマーの開始 -> WebSocket**

```
42/test-session,["start timer",10]
```

**ユーザー情報の更新 -> WebSocket**
```
42/test-session,["update users",[{"id":"***","fullname":"username","initials":"U","email":"a@example.com","gravatar":"***"}]]
```

タイマー関連の操作以外はRESTでも良さそうだが、こちらでもWebSocketを使用している。   
ほぼすべての通信をWebSocketで行っていそう。


## slackの場合

[slack](https://slack.com/)は言わずとしれたメッセージングアプリ


**メッセージの送信 -> WebSocket**
```
{"type":"message","channel":"***","text":"test","blocks":[{"type":"rich_text","block_id":"Xv56u","elements":[{"type":"rich_text_section","elements":[{"type":"text","text":"test"}]}]}], // 略
```

**チャンネルの追加 -> HTTP multipart**   
slackのチャンネル追加はかなり謎だった。slackの場合、チャンネルを作成するとWebSocketではなく、以下のようなURLに対してmultipartでなにかのデータをおくっている。

```
https://[ワークスペースの名前].slack.com/api/conversations.create
```

(ただし、チャンネルが作成されたということは、WebSocketでワークスペース内のユーザーに通知されるようだった。)  

slackほど複雑で歴史が長いと、ここでWebSocketを使いたくない理由があるのかもしれない。     
slackのユーザープロファイルの変更なども試してみたが、ほぼチャンネル追加と同じような形で実現されているみたい。

## 考察

リアルタイムな通信のためWebSocketを利用するアプリでは、チャットルームの作成のようなリアルタイムであることや通信の双方向性がそこまで必要でないものに対しても、WebSocketによる通信が使われるケースが有る。  
ただ、slackの場合には、メッセージの送信のようなリアルタイムな通信と、そうでないものは全く別のプロトコルにしていた。
これは単純に開発リソースの問題な気もする。せっかくWebSocketを使うアプリを作るのであれば、WebSocketが必須でない場面でもWebSocketを使ってしまったほうが、開発の効率は良くなりそう。    
slackレベルの複雑なアプリケーションだと、この辺の事情は変わってくるのかもしれない。

---
layout: post
title: Active StorageをAPIで使用する 
date: '2018-08-26T00:17:00.000+09:00'
author: s sato
tags:
- ruby
- rails
- active storage
---

Rails 5.2からの新機能としてActive Storageが追加された。   
例えば、Userモデルに対するアバターのイメージのようなRailsのモデルと紐づくファイルを定義できて大変便利  
また、テスト環境ではsqlite3、本番環境ではPostgreSQLのように、テスト環境ではローカルのファイルシステム、
本番環境ではAWS S3を切り替える事が出来、開発作業もとても楽になった。  

しかし、RailsをjsonのAPIサーバーとして使っている時には問題が生じる。   
以下のように、JSONはバイナリ形式のアップロードには対応していないため、JSONの要素としてイメージファイルを添付することが出来無い  
[https://stackoverflow.com/a/27504481](https://stackoverflow.com/a/27504481)  

公式のドキュメントでもこの点の対処をどうすべきか触れられていなかったので調査  

以下の調査では、以下のActive Storageのサンプルアプリケーションを使用させてもらった。  
[https://github.com/pixielabs/activestorage-example-app](https://github.com/pixielabs/activestorage-example-app)  

このサンプルでは、`users`テーブルを以下のように、`name`のみを以たシンプルなテーブルに定義している。   
 
```
create_table "users", force: :cascade do |t|
  t.string "name"
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
end
```

モデルには、以下のように`avatar`というActive Storageのファイルを持っている。  

```
class User < ApplicationRecord
  has_one_attached :avatar
  has_many_attached :documents
end
```


 ※ 以下の例では`protect_from_forgery`を抜いて、APIを実行している。
 
 
以下の様にPOSTでUserを作成する事ができる。  
 
```
$ curl -H 'Content-Type:application/json'  -XPOST localhost:3000/users.json -d '{"user":{"name": "sato"}}
{"id":3,"name":"sato","created_at":"2018-08-26T10:21:55.543Z","updated_at":"2018-08-26T10:21:55.543Z","url":"http://localhost:3000/users/3.json"}⏎
```

PUTを使えば、`name`を変更できる。  

```
$ curl -H 'Content-Type:application/json'  -XPUT localhost:3000/users/3.json -d '{"user":{"name": "changed"}}'
{"id":3,"name":"changed","created_at":"2018-08-26T10:21:55.543Z","updated_at":"2018-08-26T10:51:56.900Z","url":"http://localhost:3000/users/3.json"}⏎ 
```

JSONによるavatarの更新は不可能だが、以下のようにフォームをつかうことで、`avatar`の更新は可能だった。  

```
$ curl -XPUT localhost:3000/users/3 -F "user[avatar]=@avatar.png"
<html><body>You are being <a href="http://localhost:3000/users/3">redirected</a>.</body></html>⏎
```

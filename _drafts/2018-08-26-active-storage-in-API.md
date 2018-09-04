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
これを使う利点は以下のような感じ  
- Userモデルに対するアバターのイメージのようなRailsのモデルと紐づくファイルを定義できる  
- 特定のモデルが複数のファイルを持つ場合にも対応  
- 画像のリサイズのような前処理を入れられる。  
- テスト環境ではローカルのファイルシステム,本番環境ではAWS S3を切り替えられる。  

しかし、RailsをjsonのAPIサーバーとして使っている時には問題が生じる。   
以下のように、JSONはそもそもバイナリ形式のアップロードには対応していないため、JSONの要素としてイメージファイルを添付することが出来無い    

不可能な例:   

```
curl $host -X POST \
-d '{"users": {"name": "sato", "avatar": "[イメージデータ]"}}'
```

[参考](https://stackoverflow.com/a/27504481)  

公式のドキュメントでもこの点の対処をどうすべきか触れられていなかったので調査   


## Active Storageのサンプル

以下のActive Storageのサンプルアプリケーションを使用させてもらった。  
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

リクエスト:  
 
```
$ curl -H 'Content-Type:application/json'  -XPOST localhost:3000/users.json -d '{"user":{"name": "sato"}}
```

レスポンス:  

```
{
  "id":3,
  "name":"sato",
  "created_at":"2018-08-26T10:21:55.543Z",
  "updated_at":"2018-08-26T10:21:55.543Z",
  "url":"http://localhost:3000/users/3.json"
}⏎
```

PUTを使えば、`name`を変更できる。  

リクエスト:  

```
$ curl -H 'Content-Type:application/json'  -XPUT localhost:3000/users/3.json -d '{"user":{"name": "changed"}}'
```

レスポンス:  

```
{
  "id":3,
  "name":"changed",
  "created_at":"2018-08-26T10:21:55.543Z",
  "updated_at":"2018-08-26T10:51:56.900Z",
  "url":"http://localhost:3000/users/3.json"
}
```

## イメージのアップロード

JSONによるavatarの更新は不可能だが、上記のサンプルアプリケーションでは`avatar`の更新は可能   

```
$ curl -XPUT localhost:3000/users/3 -F "user[avatar]=@avatar.png"
```

Active Storage付きのモデルを作成する際には、以下のような流れでよさそう   

- POST users/ でユーザーを作成
- PUT users/ でavatarをアップロード

## レスポンスにイメージ格納先のURLを追加する。  

上のように、RailsをJSONのAPIに使用する場合でも、Active Storageによってファイルをアップロードすることができる。  
ただし、JSONがバイナリに対応していないため、参照系でイメージファイルをダウンロードすることはできない。  

以下の様にJSONを参照した時に、イメージ格納先のURLが表示されるようにしたい  

```
{
  "id":3,
  "name":"changed",
  "created_at":"2018-08-26T10:21:55.543Z",
  "updated_at":"2018-08-26T11:04:43.657Z",
  "url":"http://localhost:3000/users/3.json",
  "avatar_url": "[イメージのURL]" 
}
```


このために、URLを表示するためのメソッドを以下のように定義する。   

```
class User < ApplicationRecord
  include Rails.application.routes.url_helpers
  has_one_attached :avatar
  has_many_attached :documents

  def avatar_url
    avatar.attached? ?  url_for(avatar) : nil
  end

end
```

上記の`url_for`は基本コントローラーで使うurl_helperなので、モデルで使う場合には、
`include Rails.application.routes.url_helpers`が必要  

また、`url_for`で表示するURLのホスト名を`config/environments/development.rb`で設定してやる必要がある。  
(本番環境では、`production.rb`)   

```
Rails.application.routes.default_url_options[:host] = 'localhost'
Rails.application.routes.default_url_options[:port] = 3000
```

あとは、コントローラー側で、JSONを返却する際に、先程の`avatar_url`もJSONの属性として返すようにしてやる。  

```
# GET /users/1
def show
	render json: @user, methods: [:avatar_url] 
end
```

これで、以下のようなAPIになる。   


リクエスト:  

```
$ curl  localhost:3000/users/3.json 
```

レスポンス:  

```
{
    "id": 3,
    "name": "changed",
    "created_at": "2018-08-26T10:21:55.543Z",
    "updated_at": "2018-08-26T11:04:43.657Z",
    "avatar_url": "http://localhost:3000/rails/active_storage/blobs/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBDZz09IiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--e2728545eb3a8d98e8094c81cf3cedd9ac6eb0c2/avatar.png"
}
```


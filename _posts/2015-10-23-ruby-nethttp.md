---
layout: post
title: Ruby Net::HTTPの使い方と（直接）使うべきでない時
date: '2015-10-23T00:17:00.000+09:00'
author: s sato
tags:
- ruby
modified_time: '2015-10-23T01:17:09.046+09:00'
blogger_id: tag:blogger.com,1999:blog-1054230703994559763.post-366722683449831298
blogger_orig_url: http://satomemocho.blogspot.com/2015/10/ruby-nethttp.html
---


rubyで単純なHTTP Getをするのであれば、openuriが圧倒的に便利ファイルと同じように、http getリクエストを扱えてしまう。
しかし、比較的複雑なリクエスト（例：POST、ヘッダに何か入れる）の場合、net/httpを使う。

#最も単純なGET
Net::HTTPでのgetは以下のようになる。 この程度ならopenuriを使った方が良い。

```ruby
require "net/http"

#レスポンスをブロックの外で使いたい時には事前に定義しておこう
#ブロックがクロージャであることを忘れずに
response=nil

uri = URI.parse("http://example.net/")
Net::HTTP.start(uri.host, uri.port) do |http|
  response = http.get("/index.html")
  puts response.code # ステータスコード
  puts response.message # メッセージ
  puts response.body # レスポンスボディ
end

puts response.message # => OK
```

以下のようにインスタンスを作成してからコネクションを開く事もできる。
しかしこの場合には、最後にクローズしないとだめ。忘れるとシツレイ。
startにブロックを渡せば、ファイルオープンと同じように最後にクローズを勝手にやってくれるので安心。

```ruby
http = Net::HTTP.new(uri.host, uri.port)
request = Net::HTTP::Get.new("/index.html")
http.close
```

#HTTPSへのGET

以下のようにstartの引数に:use_ssl=>trueを渡してやる。

```ruby
require "net/http"

uri = URI.parse("https://example.net/")
Net::HTTP.start(uri.host, uri.port,:use_ssl=>true) do |http|
  response = http.get("/index.html")
  puts response.body
end
```

#POSTの場合

```ruby
require "net/http"

uri = URI.parse("http://example.net/")
Net::HTTP.start(uri.host, uri.port) do |http|
  response = http.post("/search.cgi",'query=foo',header=nil)
  puts response.code
  puts response.message
  puts response.body
end
```

# Net::HTTP解説のリンク

チートシート  
http://www.rubyinside.com/nethttp-cheat-sheet-2940.html

RestでJSONリクエストを投げる例。
https://www.socialtext.net/open/very_simple_rest_in_ruby_part_3_post_to_create_a_new_workspace
http://altarf.net/computer/ruby/2890

restを作る時に便利なgem  
https://github.com/rest-client/rest-client

以下に該当する場合にはNet::HTTPを使うべきでない。


単純なGETしかしない
→openuriを使う
http://ruby-doc.org/stdlib-2.1.0/libdoc/open-uri/rdoc/OpenURI.html

クローラーを作りたい  
→anemoneを使う  
https://github.com/chriskite/anemone

Amazonの商品検索、操作APIを使いたい
→asinを使う
https://github.com/phoet/asin

AWSのRESTを使いたい
→aws-sdk-rubyを使う
https://github.com/aws/aws-sdk-ruby

なんかRESTを使いたい。
→rest-clientを使う
https://github.com/rest-client/rest-client


---
layout: post
title: http://go/somewhereのようなショートカット
date: '2020-02-06T00:00:00.000+09:00'
author: s sato 
tags:
- go
---

従業員がイントラネット内でネットサーフィンをするのは結構大変だ。
企業のイントラネット内のサイトはインターネット上に公開するわけにもいかず
普通は検索エンジンに乗らない。
当然googleで勤怠と検索しても自社の勤怠管理用のサイトは出てきてくれない。
イントラネット内にDNSサーバーがあれば、
管理者が`http://kintai.internal.companyA.com`のような形で従業員用の勤怠管理サイトの
名前を登録してくれているかもしれない。
しかし、このようなURLはおぼえられるほど短くないし、
予算管理は、`http://internal.companyA.com/cooporate/a/b/c/yosan.html`
のような全然別のURLにあるのかもしれない。大きな企業になればなるほどこの辺の統制は
難しいと思う。  
結局は昔ながらのリンク集のようなものに頼ることがほとんどなのではないだろうか？  

一方で、ソースを忘れてしまったがgoogle社内では `http://go/kintai `みたいなURLで社内向けのサイトへのアクセスを
簡単にできるようにしているらしい。(実際は英語だろうけど)


![go/kintai]({{ site.url }}/assets/gokintai.PNG)

ここまで短ければ容易に覚えられるし、ただのURLのパスなので名前の競合を心配する必要もない。
`http://internal.companyA.com/cooporate/a/b/c/yosan.html`のような
コーポレート部門の作った複雑な予算管理Webサイトにも`http://go/yosan`で重要なところだけアクセスすることが出来る。  


### "go"がドメイン名として使用できるか？

`***.com`や`***.co.jp`ではなく`go`なんていうドメイン名をパブリックなDNSに登録するのは
さすがに無理。そもそも、ドットすら入っていない。。。  
だが、以下のようなエントリをhostsファイルに登録した状態でブラウザのurlに`go`
と入力すると普通にlocalhostに対してリクエストを出してくれた。

```
127.0.0.1 go
```

ということは、`localhost:80`(`go:80`)にサーバーを立ち上げ、何らかの形で`go/somewhere`
へのリクエストをどこかに転送すれば、google風のショートカットができるはずだ。
せっかく`localhost`に立てるので、`localhost/bank`(`go/bank`)で自分の使っている
銀行口座のログインページに行くようなブックマークのようもできるようにしたい。  


### Nginxを使う？

`go/somewhere=(localhost/somewhere)`へのリクエストをどこか別の場所に
送るだけであれば、NginxやHAProxyなどの設定をいじって立ち上げれば十分にできる。  
だが、以下のような制御をいれたいので、Go(プログラミング言語)で作ってみることにした。  

- `go/smewhere`のようなスペルミスをしても大丈夫なようにしたい
- どのパスがどのサイトに行くかをyaml(読みやすい)にしたい
- 設定ファイルが変わったら自動で再読み込みしたい
- `go/`になんか出したい。(リンクの一覧とか)

### リバースプロキシ(失敗)

実装の際、最初に思ったのは、このサーバーは`go/a`へのリクエストを`websiteA.com`、
`go/b`へのリクエストを`websiteB.com`に送信した結果をクライアントに戻す
リバースプロキシのようなものになるんじゃないかということだった。  

だが、ちょっと実装してみてダメだということが分かった。  
`websiteA.com`のページ内での`/index.js`へのSame Originのリクエストが`go/index.js`に行ってしまう。
これを`websiteB.com`から`/index.js`へのリクエストと見分ける手段がない。ブラウザがSame Originの
リクエストに対しても必ずRefererヘッダーをつけるようなことをしてくれれば、見分けることが出来るが
ブラウザ側に手をいれるのは、社内のショートカットへの利用を想定するとなるべく避けたい。

### リダイレクトを使う

結局`go/a`へのリクエストを`websiteA.com`にリダイレクトするような
サーバーにすることにした。これならずっとシンプルだし、ヘッダーとかの余計なことを
考えなくても済む。  
Go(言語)でのリダイレクトは以下に簡単なサンプルがあった。  
https://gist.github.com/hSATAC/5343225  

この例を少しだけ改造して複数のリダイレクト先をPathに応じて選ぶようにすると以下のようになる。

```go
package main

import (
	"log"
	"net/http"
	"strings"
)

var destinations map[string]string

func init() {
  // パスとその時のリダイレクト先
	destinations = map[string]string{
		"shop": "https://amazon.com",
		"bank": "https://www.smbc-card.com/mem/index.js",
	}
}

// r.URL.pathは`/shop`だったり、`/shop/`だったりするので、
// ここで`/`をトリムする
func getDestination(path string) (string, bool) {
	// Remove slash if exists
	d := strings.TrimPrefix(path, "/")
	d = strings.TrimSuffix(d, "/")
	destination, found := destinations[d]
	return destination, found
}

func redirect(w http.ResponseWriter, r *http.Request) {
	destination, found := getDestination(r.URL.Path)
	if found {
		http.Redirect(w, r, destination, 301)
	} else {
		http.NotFound(w, r)
	}

}

func main() {
	http.HandleFunc("/", redirect)
	err := http.ListenAndServe(":80", nil)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}
```

上のサーバーをlocalhostに立てると、`localhost/shop`を`amazon.com`に`localhost/bank`を`www.smbc-card.com/mem/index.js`にリダイレクトしてくれる


### リダイレクトのステータスコード

上の例だとリダイレクトのステータスコードに問題があった。ステータスコード301はMoved Permanently
なので、恒久的なサイトの移動があることを指す。
`localhost/shop`が一旦`amazon.com`に301でリダイレクトすると、ブラウザ(すくなくともChrome)
は`localhost/shop`への次のアクセス時に`localhost/shop`へのリクエストを出さずに、
キャッシュされた結果から永久に`amazon.com`に直接行ってしまう。これでは`localhost/shop`の行き先を
`www.rakuten.co.jp`に変更したい場合などに困ってしまう。  

この挙動はCache-Controlヘッダーで制御できないこともないが、意味論的にただしい307(Temporary Redirect)
を用いるのがよさそうだ。307の場合はブラウザは毎回`localhost/shop`にアクセスしてくれる。  


### パスにあいまいさを持たせる

先ほどの例だと、以下のようにリダイレクト先の決定は行き先のMAP(`map[string][string]`)
にリクエストのパスがあるかどうかだった。

```go
	destination, found := destinations[d]
	return destination, found
```

これだと、`localhost/shopp`のような打ち間違いをした場合にエラーになるしかない。  
以下のように編集距離が最も短い宛先にリダイレクトするようにしてみた。
(編集距離の導出は[github.com/agnivade/levenshtein](https://github.com/agnivade/levenshtein)を利用)

```go
	var destination string
	minDistance := math.MaxInt32
	for k, v := range destinations {
		distance := levenshtein.ComputeDistance(k, d)
		if distance < minDistance {
			minDistance = distance
			destination = v
		}
	}

	if minDistance < 3 {
		return destination, true
	} else {
		return "", false
	}
}
```

だが、単純な編集距離だと、`localhost/shopping`と`localhost/card`があった際に
`localhost/sho`と入力された場合、`localhost/shopping`(編集距離:5)よりも`localhost/card`(編集距離:4)が優先されてしまう。  
もうちょっとよいアルゴリズムがありそう。。。
 

### 完成

一応最小限の機能がそろったので、[github.com/sato-s/gosomewhere](https://github.com/sato-s/gosomewhere)
に上げてみた。  
(yaml自動リロードや、`go/`に何か出すのは未対応)  


インストール  

```bash
go get -u github.com/sato-s/gosomewhere

# 設定ファイルを作る
cat << EOF > config.yaml
port: 80
listen: 0.0.0.0
destinations:
  shop: https://www.amazon.com/
  credit: https://www.smbc-card.com/mem/index.jsp
  search: https://www.google.co.jp
  vim: https://vim.rtorr.com/
  ascii: https://en.wikipedia.org/wiki/ASCII#Printable_characters
  cloud: https://developers.digitalocean.com/documentation/v2/
EOF
```

起動(port:80を使うから用sudo)  

```bash
sudo env "PATH=$PATH" gosomewhere config.yaml
```


確認(事前にhostsに`go`を登録)  

```bash
curl -v go/shop
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to go (127.0.0.1) port 80 (#0)
> GET /shop HTTP/1.1
> Host: go
> User-Agent: curl/7.61.1
> Accept: */*
>
< HTTP/1.1 307 Temporary Redirect
< Content-Type: text/html; charset=utf-8
< Location: https://www.amazon.com/
< Date: Sun, 09 Feb 2020 04:07:24 GMT
< Content-Length: 59
<
<a href="https://www.amazon.com/">Temporary Redirect</a>.
```

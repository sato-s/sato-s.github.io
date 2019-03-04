---
layout: post
title: テキストの折りたたみと動的計画法
date: '2019-03-04T00:00:00.000+09:00'
author: s sato
tags:
- elixir
- algorithm
---

[MIT Open Course](https://www.youtube.com/watch?v=ENyox7kNKeY&list=WL&index=34&t=0s)を見ていたら、テキストの折りたたみに動的計画法を利用する方法が紹介されていた。  
動的計画法といえば、大学の時にナップザックを問題はならったが、いまいち何の役に立つのかよくわからないものだった、実際に使えそうな例を紹介してくれるとは流石MIT。  

というわけで実装してみた。折角の動的計画法なので、関数形言語のelixirでBottom-upのアプローチを取ってみる。  

### ”良い”テキストの折り返しとは？

以下のようなテキストを幅6のウィンドウ内で折り返す場合を考える  

```
aaa bb cc dddddd
```

各行を7文字以内で折り返すために、考えられるもっとも単純な方法は、
テキストの初めから単語を取り出していき、
取り出した単語を現在の行に追加して7文字を超えなければ、そのまま追加し、6を
超えるようであれば改行を加え新しい行に入れていくというものだ。  
この手順を実行すると上の文字列は次の様に折り返すことができる  
(以下の例では6文字以下の余計な空白を•で表す)  

```
aaa bb
cc••••
dddddd
```

上の例の折り返しで各行を6文字以下にすることができているが、あまり良いとは言えない。
なぜなら、2行目に2文字しか入っておらず全体的なバランスが崩れてしまっているからだ。  
以下のように折り返した方が全体的なバランスとしてはよい。  

```
aaa•••
bb cc•
dddddd
```

### 評価関数の導入

"良い"テキストの折り返しのためには、行数を最小にしつつも、テキスト全体で余白の数が均等になっている必要がある。  
このため、各行の余白の数の3乗を合計したものを評価関数とする。  

例えば、以下のテキストの場合、

```
aaa bb
cc••••
dddddd
```

\\(  1行目の余白^3 + 2行目の余白^3 + 3行目の余白^3 = 0^3 + 4^3 +0^3 = 64\\)

となる。   
一方で、以下のテキストの場合には

```
aaa•••
bb cc•
dddddd
```

\\(  1行目の余白^3 + 2行目の余白^3 + 3行目の余白^3 = 3^3 + 1^3 +0^3 = 28\\)

となり、先ほどの値より小さい。  
バランスよく折り返しを入れてやるためには、各行の余白の数の3乗の合計値を最小化するようにテキストを配置してやればよい。  

### 文字列の取り扱い

これからの計算では、文字列の中身ではなく、各文字の長さが重要になってくる。  
そこで、基本的に文字列は、各単語の長さの配列として扱う。  
これはelixirでは以下のように計算することが出来る。  

```elixir
"aaa bb cc ddddd"
  |> String.split(" ")
  |> Enum.map(&String.length/1) # => [3, 2, 2, 5]
```

今後この長さの配列を`lengths`という名前の変数として扱う。  

### 余白の計算

評価関数を計算するためには、まず余白の数をカウントする必要がある。  
そこで、`lengths`の`from`番目から`to`番目の要素を1行に入れた際の余白の数を返す、`trailing_white_spaces`という関数を考えてみる。  
後々にメモ化を行い動的計画法を適用するためにこの関数は再帰関数にする必要がある。  
再帰関数を定義するため、まず初期値、つまり`from`と`to`が両方0の場合を考えてみる。  
この場合、`lengths`の0から0番目の要素(つまり1番最初のワード)を取り出して、余白をカウントすればよい。  
テキスト用のウィンドウの幅を`@limit`と置くと、以下のように、`@limit`から、1番最初のワードの長さを引けばよい。  

```elixir
defmodule TextFolding do
  @limit 30
  def trailing_white_spaces(lengths, from, to) when from == 0 and to == 0 do
    @limit - Enum.at(lengths, 0)
  end
end
```

だが、よくよく考えてみると、1から1番目の要素を取り出した際も、2から2番目の要素を取り出した際も、出てくるワードは1個だけなので、  
計算方式は上の場合と全く同一だ。結局、以下のように定義することが出来る。  

```elixir
defmodule TextFolding do
  @limit 30
  def trailing_white_spaces(lengths, from, to) when from == to do
    @limit - Enum.at(lengths, from)
  end
end
```

次に、`to`がnの時に、`to`がn-1の時の`trailing_white_spaces`の結果を使って、nの場合の計算をする方法を考えてみる。  
余白が`trailing_white_spaces(lengths, from, to - 1)`個ある行に対してに`to`番目のワードを付け加えるため、残りの余白の数は、以下のような関数で表すことが出来る。  

```elixir
def trailing_white_spaces(lengths, from, to) when from != to do
  trailing_white_spaces(lengths, from, to - 1) - Enum.at(lengths, to) - 1
end
```

上で、`-1`が余計に引かれているのは、n-1までのワードの末尾に、余白を追加してから、新しいワードを追加しているからだ。  
(`aaa`に`bbb`を追加した際は、`aaabbb`ではなく、`aaa bbb`にした時に余白をカウントする必要がある。)  
また、この関数はマイナスの値を返すこともあるが、そのケースは評価関数のなかで考慮することにする。  


結局`trailing_white_spaces`関数は以下のようになる。  

```elixir
defmodule TextFolding do
  @limit 30
  def trailing_white_spaces(lengths, from, to) when from == to do
    @limit - Enum.at(lengths, from)
  end

  def trailing_white_spaces(lengths, from, to) when from != to do
    trailing_white_spaces(lengths, from, to - 1) - Enum.at(lengths, to) - 1
  end

  # 不正な値を防ぐため念のため追加
  def trailing_white_spaces(_, from, to) when from > to do
    raise "Something is very wrong"
  end
end
```

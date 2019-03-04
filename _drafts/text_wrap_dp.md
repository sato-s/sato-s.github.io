---
layout: post
title: テキストの折り返しと動的計画法
date: '2019-03-04T00:00:00.000+09:00'
author: s sato
tags:
- elixir
- algorithm
---

[MIT Open Course](https://www.youtube.com/watch?v=ENyox7kNKeY&list=WL&index=34&t=0s)を見ていたら、
テキストの折り返しに動的計画法を利用する方法が紹介されていた。
動的計画法といえば、大学の時にナップザックを問題はならったが、いまいち何の役に立つのかよくわからないものだった、実際に使えそうな例を紹介してくれるとは流石MIT。  

というわけで実装してみた。折角の動的計画法なので、関数形言語のelixirでBottom-upのアプローチを取ってみる。  

### ”良い”テキストの折り返しとは？

以下のようなテキストを幅6のウィンドウ内で折り返す場合を考える  

```
aaa bb cc dddddd
```

各行を6文字以内で折り返すために、考えられるもっとも単純な方法は、
テキストの初めから単語を取り出していき、
取り出した単語を現在の行に追加して6文字を超えなければ、そのまま追加し、6を
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
テキスト用のウィンドウの幅を`@limit`と置くと、`@limit`から取り出したワードの幅を引いた値が残りの余白なので、以下のようになる。  

```elixir
defmodule TextWrap do
  @limit 30
  def trailing_white_spaces(lengths, from, to) when from == 0 and to == 0 do
    @limit - Enum.at(lengths, 0)
  end
end
```

だが、よくよく考えてみると、1から1番目の要素を取り出した際も、2から2番目の要素を取り出した際も、出てくるワードは1個だけなので、
計算方式は上の場合と全く同一だ。結局、以下のように定義することが出来る。  

```elixir
defmodule TextWrap do
  @limit 30
  def trailing_white_spaces(lengths, from, to) when from == to do
    @limit - Enum.at(lengths, from)
  end
end
```

次に、`to`がnの時に、`to`がn-1の時の`trailing_white_spaces`の結果を使って、nの場合の計算をする方法を考えてみる。
余白が`trailing_white_spaces(lengths, from, to - 1)`個ある行に対してに、新たなワードを加えると、余白の数は
新なワードの幅＋1だけ減るはずだ。  
(`aaa`に`bbb`を追加した際は、`aaabbb`ではなく、`aaa bbb`にした時に余白をカウントする必要がある。)  
このため、以下のように、`to-1`の場合の余白の数から`to`番目のワードの幅＋1を引く関数になる。

```elixir
def trailing_white_spaces(lengths, from, to) when from != to do
  trailing_white_spaces(lengths, from, to - 1) - Enum.at(lengths, to) - 1
end
```

結局`trailing_white_spaces`関数は以下のようになる。  

```elixir
defmodule TextWrap do
  @limit 30
  def trailing_white_spaces(lengths, from, to) when from == to do
    @limit - Enum.at(lengths, from)
  end

  # 不正な値を防ぐため念のため追加
  def trailing_white_spaces(_, from, to) when from > to do
    raise "Something is very wrong"
  end

  def trailing_white_spaces(lengths, from, to) when from != to do
    trailing_white_spaces(lengths, from, to - 1) - Enum.at(lengths, to) - 1
  end
end
```

この関数はマイナスの値を返すこともあるが、そのケースは評価関数のなかで考慮することにする。  

### 1行の評価関数

`from`から`to`番目までの文字の余白の数は`trailing_white_spaces(lengths, from, to)`で計算できるようになったので、
今度はその関数を使って、`from`から`to`までの文字を1行に配置した際の、その行のコストを求める。`line_cost`
を定義してみる。  

```elixir
defmodule TextWrap do
  @infinity 100_000_000_000
  def line_cost(lengths, from, to) do
    if trailing_white_spaces(lengths, from, to) < 0 do
      # Return (almost) infinity cost if words in from-to can't arrange in one line.
      @infinity
    else
      :math.pow(trailing_white_spaces(lengths, from, to), 3)
    end
  end
end
```

上のように、単純に余白の数を3乗した値がコストになる。
ただし、`trailing_white_spaces`で計算した余白の数はマイナスになることがあるので、その場合にはほぼ無限に大きなコストを返すようにしている。  

### 評価関数の最小化

ここまでで、`from`番目から`to`番目までのワードを1行に配置した時の評価をすることができるようになった。
次に、この関数を使って、0からn番目までのワードの最小のコストをもとめる関数`cost`を考えてみる。
コストだけを求めても実際の折り返しができない。実際に折りたたんだ文字列を出力するために`cost`関数はコストと折り返し位置の配列の両方を返却するようにする。  
この関数も先ず、初期値(n=0)の場合を考えてみる。  
n=0の場合はシンプルに計算できる。コストとしては、`line_cost`を使って、0から0番目までの文字列のコストを計算すればよい。
また、折り返し位置に関しても、まだ1ワードしかないので、折り返しようがないため単純に空の配列を返却すれば良い。  

```elixir
def cost(lengths, n) when n == 0 do
  {TextWrap.line_cost(lengths, 0, 0), []}
end
```

次に、nの場合の`cost`をn-1のコストを求める必要があるがこれはそこまでシンプルではない。  
次のようなn-1番目までの文字列に新たにn番目の文字`cc`を加える場合のことを考えてみる。  

```
aaa bb
```

上に対して`cc`を付け足すには、"新しい行として付け足す"か"同じ行に付け足す"かの2つの選択肢がある。  
"同じ行に付け足す"場合の文字列は以下のように1行になるので、`line_cost(lengths, 0, n)`で求めてやればよい。  

```
aaa bb cc
```

"新しい行として付け足す"場合には文字列は以下のようになる。

```
aaa bb
cc
```

この場合のコストは、`aaa bb`までの最小コストである`cost(lengths, 0, n -1)`に`cc`の行のコストである`line_cost(lengths, n, n)`をたすことで計算することができる。  
しかし、これだけでは、まだ考慮が不十分だ。  
n-1番目までの最小コストの文字列は`aaa bb`だったが、だからと言って、n番目で必ずしも`aaa bb`の文字列の並びを採用できる訳ではない。  
以下のように、n-1番目までは最小コストで無かった並びに対して、`cc`を加えた場合に関しても検討する必要がある。  

```
aaa
bb
```

実際にウィンドウ幅が6の時を考えてみると、以下のように上記に`cc`を付け足した場合のコストは、
\\((6-3)^3 + (6-5)^3 = 28\\)であり、上で検討した2パターンよりも小さい。

```
aaa
bb cc
```

このため、  
\\( cost(n)=\\\
Min(linecost(0,n), cost(0) + linecost(1,n), cost(1) + linecost(2,n) .. ,cost(n-1) + linecost(n-1, n-1) ) \\)


```elixir
def cost(lengths, n) do
  costs = (0..n-1)
    |> Enum.map(
      fn(wrap) ->
        {prev_cost, prev_wrap} = cost(lengths, wrap)
        new_line_cost = TextWrap.line_cost(lengths, wrap + 1, n)
        cost = prev_cost + new_line_cost
        wraps = prev_wrap ++ [wrap]
        {cost, wraps}
      end)
  one_line_cost = {TextWrap.line_cost(lengths, 0, n), []}
  [one_line_cost | costs]
    |> Enum.min_by(fn({cost, _wraps}) -> cost end)
end
```

---
layout: post
title: RubyのArray#unshiftが速すぎる件と償却解析
date: '2019-07-23T00:00:00.000+09:00'
author: s sato
tags:
- ruby
- algorithm
---

プログラミング言語によって呼ばれ方はさまざまであるが、rubyにおいて`push`は
Arrayの最後尾にあらたな要素を付け足す処理を指す。   

```ruby
a = [1,2,3,4,5]
a.push('push')
puts a # => [1, 2, 3, 4, 5, 'push']
```

Linked Listではなく、Arrayという名前が付いているということは、格納された要素はメモリ上で連続した領域に配置されている必要がある。
この時、問題になるのがメモリの確保のやり方だ。   

```ruby
a = []
a.push('push')
a.push('push')
a.push('push')
a.push('push')
```

上の様にArrayに対して1個ずつ要素が追加されていった際に、`push`が呼ばれるたび新なArrayのためのメモリを確保していたのでは、`push`のたびにmallocが
動作することになり、非常に効率が悪い。  
そこで、ruby(やその他のプログラミング言語)では、以下のように要素の追加によってArrayの領域の拡張の必要が生じた際に、現在の要素数の倍の領域を
確保しておき、将来の更なる要素の追加に備えるというやり方が取られている。  

![array-push]({{ site.url }}/assets/array_push_double.svg)

このようにメモリ確保という遅い操作を避け、平均的な計算量を下げる最適化は[償却解析](https://ja.wikipedia.org/wiki/%E5%84%9F%E5%8D%B4%E8%A7%A3%E6%9E%90)と呼ばれる。


## unshiftの計算量

一方で`unshift`は、以下のように配列の先頭に要素を付け足す動作を指している。  

```ruby
a = [1,2,3,4,5]
a.unshift('unshift')
puts a # => ['unshift', 1, 2, 3, 4, 5]
```

この場合には、`unshift`を実行するたびに新な要素を先頭に加えたArray全体の領域をmallocするので`push`の場合
と比較して配列の要素が大きくなるほど、計算時間が大きくなっていくような気がする。  

![array-unshift]({{ site.url }}/assets/array_unshift.svg)

ところが、実際はそうではなかった。
以下のようなコードで確認してみると実行結果は、`push`が0.09秒に対して、`unshift`が0.08秒で、実行時間に大差はなかった。

```ruby
a = []
t = Time.now
1_000_000.times{a.unshift(1)}
puts "unshift: #{Time.now - t}"

a = []
t = Time.now
1_000_000.times{a.push(1)}
puts "push: #{Time.now - t}"
```

これはかなり予想外の結果だった。確認のためjavascriptとpythonで同様の比較を試してみると`unshift`は`push`に較べて明らかに
低速で、rubyの`unshift`が異常に速い事が分かる。  


| 言語                      | push   | unshift |
| :------:                  | :----: | :----:  |
| ruby (MRI 2.6.0)          | 0.09   | 0.08    |
| javascript (node v12.2.0) | 0.04   | 251.47  |
| python (c-python 3.7.2)   | 0.12   | 331.53  |


(pythonの場合は、`push`,`unshift`という名前のメソッドではなく`append`,`insert`)  

## unshiftの償却解析

調べてみるとRuby 2.0.0(MRI)から以下のコミットで`unshift`に対しても償却解析が導入されていた。  
[https://github.com/ruby/ruby/commit/fdbd3716781817c840544796d04a7d41b856d9f4](https://github.com/ruby/ruby/commit/fdbd3716781817c840544796d04a7d41b856d9f4)

肝になるのが、以下の`ary_ensure_room_for_unshift`関数になる。  

```c
static VALUE
ary_ensure_room_for_unshift(VALUE ary, int argc)
{
    // 中略
    if (head - sharedp < argc) {
        long room;
      makeroom:
        room = capa - new_len;
        room -= room >> 4;
        MEMMOVE((VALUE *)sharedp + argc + room, head, VALUE, len);
        head = sharedp + argc + room;
    }
    // 中略
}
```

この関数では、`unshift`が実行されたが、先頭に追加するための領域が存在しない時
`MEMMOVE`で、既存のArrayの内容を`sharedp`(実際のデータが入る領域のポインタ)から、`argc`(unshiftで付け足す要素の個数)と`room`(将来のunshiftに備えた領域)の分だけ余裕を持たせた位置に格納している。  

このように`unshift`の場合も償却解析されている事実は`unshift`していった際のArrayのサイズを以下のように見ていくことでも別る。

```
[5] pry(main)> a = []
=> []
[6] pry(main)> ObjectSpace.memsize_of(a)
=> 40
[7] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 40
[8] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 40
[9] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[10] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[11] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
[12] pry(main)> ObjectSpace.memsize_of(a.unshift(1))
=> 192
```

`unshift`での償却解析はArrayクラスをキュー(unshiftが頻繁に必要になる)として使用する場合を想定して行われた様だ。  
細かな工夫だが場合によっては劇的にパフォーマンスを改善してくれる修正だ。rubyコミュニティすごい 


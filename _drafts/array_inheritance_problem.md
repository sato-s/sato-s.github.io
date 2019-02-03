---
layout: post
title: Array継承問題
date: '2019-01-24T00:17:00.000+09:00'
author: s sato
tags:
- ruby
- javascript
- python
---

## Enumerableを使った設計

rubyにEnumerable、pythonにIterableという仕組みがある。  
これらはいずれも、イテレート可能なオブジェクトを作るための機能になっている。  

例:  

*`Accounts#to_table`は複数の`Account`をHTMLテーブルに変換するメソッド、内部で`Account#to_tr`を呼び出し各`Account`を行に変換している*

```ruby
class Account
  attr_reader :id, :age

  def initialize(id, age)
    @id = id
    @age = age
  end

  def child?
    @age < 20
  end

  def to_tr
    <<~TR
      <tr>
        <td>#{@id}</td>
        <td>#{@age}</td>
      </tr>
    TR
  end

end

class Accounts
  include Enumerable

  def initialize(_accounts)
    @_accounts = _accounts
  end

  def each
    @_accounts.each{|account| yield account}
  end

  def average_age
    @_accounts.map(&:age).sum / @_accounts.size
  end

  def to_table
    <<~TABLE
      <table>
        <tr>
          <th>ID</th>
          <th>AGE</th>
        </tr>
        #{@_accounts.map(&:to_tr).join}
        <tr>
          <td>Average</td>
          <td>#{average_age}</td>
        </tr>
      </table>
    TABLE
  end

end

accounts = Accounts.new((1...5).map{|id| Account.new(id, rand(100))})
puts accounts.to_table
```


結果:  

{% include sample_table.html}

上の例では、`Accounts`と`Account`という2つのクラスを定義している。  
`Accounts`には、上記の`#average_age`や`#to_table`のような**複数の**`Account`に固有の処理を実装することが出来る。  
単に複数の`Account`をArrayにいれるだけでももちろんイテレーションは可能だが、
この場合、`AccountsSerializer`や`AccountsHelper`のようなモジュールを別途定義し、
そこで、平均年齢の計算や`table`への変換を実装することになるだろう。  
EnumerableやIterableをつかった設計は、そういった設計よりもオブジェクト指向的で理解しやすいものになると個人的にはおもう。  

## Enumerable,Iterableの問題点

便利なEnumerableだが、問題もある。  


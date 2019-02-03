---
layout: post
title: Enumerable,Iterableを使った設計
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
自分はこのEnumerable,Iterableを使用して、`Accounts(複数形)`,`Account(単数形)`のように複数形と単数形のクラスを作成するという設計を頻繁に用いる。  
`Account(単数形)`は、誰が作ったとしても`#name`や、`#id`のようなアカウントの属性用のゲッターや、`#valid?`,`#child?`のようなメソッドを持つことになるだろう。
  
問題は、複数のアカウントにまたがる処理だ、例えば複数のアカウントをJSONやHTMLに変換したり、アカウントの平均年齢などの統計情報の取得などになる。  
これは、Enumerableを使う人と使わない人によって2パターンに分かれる。  
Enumerableを使う場合には、次のような設計になるだろう  

例:  
複数のアカウントをHTMLテーブルに変更するプログラム   

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

上の例では`Account(単数形)`は、`id`と`age`という属性と、2つのメソッドを持っている。  
`#child?`は、そのアカウントが子どもかどうかを判定するメソッド、`#to_tr`は、そのアカウントをHTMLテーブルの`<tr>(行要素)`に変換するメソッドだ。  
`Accounts`には、上記の`#average_age`や`#to_table`のような**複数の**`Account`に固有の処理を実装している。  


## Enumerable,Iterableを使わない場合

一方で、`Enumerable`を使わなくても当然このような処理を書くことはできる。  
この場合、`AccountsRenderer`や、`AccountsHelper`の様なモジュールを定義することになるだろう。  

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

end

module AccountsRenderer
  module_function
  def render(accounts)
    average_age = accounts.map(&:age).sum / accounts.size
    <<~TABLE
      <table>
        <tr>
          <th>ID</th>
          <th>AGE</th>
        </tr>
        #{accounts.map{|account| _account_to_tr(account)}.join}
        <tr>
          <td>Average</td>
          <td>#{average_age}</td>
        </tr>
      </table>
    TABLE
  end

  def _account_to_tr(account)
    <<~TR
      <tr>
        <td>#{account.id}</td>
        <td>#{account.age}</td>
      </tr>
    TR
  end
end

accounts = (1...5).map{|id| Account.new(id, rand(100))}
puts AccountsRenderer.render(accounts)
```

## Enumerableを使う意義

どちらが正しいとも言うことができないが、よりオブジェクト指向的なのは、Enumerableを使った場合だ。  
`Accounts`というモノ、`#average_age`や、`#to_table`のようなメソッドをもつというのは、現実世界のモデル化という意味で分かり易い。  
一方で`AccountsRenderer`というのは、現実世界に存在しない少し抽象的な概念だ。`Accounts`のケースに比べると直観的な理解のしやすさという点では劣っているように思う。  
また、HTMLだけでなく、JSONやその他の形式に変更したくなった場合、それらに共通の処理の場所も問題になる。  


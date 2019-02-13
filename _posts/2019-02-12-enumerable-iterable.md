---
layout: post
title: Enumerable,Iterableを使った設計
date: '2019-02-12T00:00:00.000+09:00'
author: s sato
tags:
- ruby
- python
---

## Enumerable,Iterableとは

rubyにEnumerable、pythonにIterableという仕組みがある。  
これらはいずれも、イテレート可能なオブジェクトを作るための機能だ。  
例えば、rubyでは以下のように、Enumerableなクラスを作ることができる。  

```ruby
class MyIntegers
  include Enumerable

  def initialize(_integers)
    @_integers = _integers
  end

  def each
    @_integers.each{|i| yield i}
  end

end

integers = MyIntegers.new([1, 2, 3, 4, 5, 6, 7, 8 ,9, 10])

p integers.select(&:even?) # => [2, 4, 6, 8, 10]
p integers.sum # => 55
p integers.reduce(&:*) # => 3628800
```

上の様に、rubyではEnumerableをIncludeした後に、`#each`メソッドを定義し、そこで、イテレーションの対象を`yield`してやることで、Enumerableなクラスが作成できる。  
`#each`を実装したことによって、`#select`、`#sum`,`#reduce`などの、Enumerableなクラスに特有のメソッドが自動的にクラスに追加され利用可能になる。  

pythonの場合には、以下の様に、`__iter__`と`__next__`メソッドを実装すると言う形で、Iterableなクラスを作る事ができる。  

```python
# -*- coding: utf-8 -*-

from functools import reduce
class MyIntegers:
    def __init__(self, _integers):
        self._integers = _integers
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > len(self._integers) - 1:
            raise StopIteration
        else:
            self.current += 1
            return self._integers[self.current - 1]

integers = MyIntegers([1, 2, 3, 4, 5, 6, 7, 8 ,9, 10])

print(list(filter(lambda i: i % 2 == 0, integers))) # => [2, 4, 6, 8, 10]
integers.current = 0 # reset iterator
print(reduce(lambda i,acc: i + acc, integers, 0)) # => 55
integers.current = 0
print(reduce(lambda i,acc: i * acc, integers)) # => 3628800
```

## Enumerableを使った設計

`#sum`,`#reduce`,`#select`などのメソッドを使いたいだけであれば、Arrayのなかに、値を入れてしまえばいいだけである。   
例えば、以下のコードは問題なく動作する。  

```ruby
integers = [1, 2, 3, 4, 5, 6, 7, 8 ,9, 10]

p integers.select(&:even?) # => [2, 4, 6, 8, 10]
p integers.sum # => 55
p integers.reduce(&:*) # => 3628800
```

Enumerableを使う意義は、Arrayの標準的なメソッド以外を自分で定義できる点にあると思う。  
もう少し実用的な例として、複数のアカウントをHTMLテーブルに変更するプログラムを考えてみる。   

例:  

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

{% include sample_table.html %}

上の例では、`Accounts(複数形)`が`Account(単数形)`を抱えるEnumerableとして定義されている。  
単体のアカウントをテーブルのレコードに変換する処理は`Account(単数形)`に定義されており、
複数のアカウントをテーブルに治す処理や、複数のアカウントの平均年齢を求める処理は、`Accounts(複数系)`に定義することができる。  
複数のアカウントに関する処理もメソッド呼び出しの形式で掛けるのでよりオブジェクト志向なコーディングができると思う。  

なお、Enumerableを使わずに同様の処理するならば、以下のように、`AccountsRenderer`の様なモジュールを定義することになるだろう。  

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

このような設計もよくあるものだが、オブジェクト指向原理主義としては、やはりEnumerableを使った方が気持ちがいい。  

## Enumerableの問題点

便利なEnumerableだが不満点もある。  
それは、自動的に追加されたメソッドを読んだ場合に、Arrayが帰ってきてしまうという問題だ。  

```ruby
class Account
  attr_reader :age

  def initialize(age)
    @age = age
  end

  def child?
    @age < 20
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

end

accounts = Accounts.new((1...5).map{Account.new(rand(100))})

accounts.select(&:child?).class # => Array
accounts.select(&:child?).average_age # => Method Missing!
```

例えば、上の例では、`Accounts`に対して、`#select`を呼び出した後に返却されるのは、`Accounts`ではなく、`Account`のArrayになっている。  
このため、`#select`された結果に対して`#average_age`を呼び出そうとすると、エラーになってしまう。  

これを防ぐためには、以下のように、自前の`#select`で、Arrayを`Accounts`に変換してから返却する必要がある。  

```ruby
class Accounts
  include Enumerable

  # 略

  # この部分を追加
  def select(*args, &block)
    self.class.new(@_accounts.select(*args, &block))
  end

end
```

同様のArrayを返すメソッドは他にもあり、`#drop`、`#take`、`#reject`あるいは、オペレーターの`+`や`|`も同じ様に`self.class.new`でラップすれば、対応できる。  
メタプログラミングで、Arrayを返すメソッドは全部、ラップしてやればいいのではと思ったが、`#group_by`,`#partition`,`#chunk`など、単純には対応できないメソッドがけっこうある。  
また、`#map`や、`#to_a`などは、そもそも、Arrayを返す挙動にしておくのが正しい対応だろう。  
結局、`#select`などの使うメソッドだけ、自分で望ましい形に定義してやるのがいいのかもしれない。  

## まとめ

- Enumerable,IterableでよりよいOOP
- 自動で定義されたメソッドの内、Arrayを返却するのもは、状況に応じて自分で再定義する



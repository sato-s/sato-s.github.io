---
layout: post
title: yield selfによるVagrantfile風の設定ファイル
date: '2016-07-13T23:19:00.000+09:00'
author: s sato
tags:
- ruby
---

自作のモジュールを作成する際に、挙動を変えるためにユーザーに設定ファイルを提供しなければならない場合がある。  
どのような設定ファイルにすべきかの選択肢はいくつか考えられる。


- xmlを使う  
テキストエディタから編集しずらく、読みにくい。誰もがxmlエディタを持っている訳ではない。
diffをとっても何が変わったかわかりずらくgitからの管理に向かない。
- jsonを使う  
xml同様読みずらい。
- parameter = values  のような自作の設定ファイル  
最悪の選択肢。パーサーを自作する必要がある。良く作り込まなければ、ユーザーがスペースの
数やタブ区切りかスペース区切りかを意識する必要がある。
また文字コード、改行コードの違いで上手く動作しない可能性もある
- yamlを使う  
読み易く、gitからも管理しやすい。  
でも複雑な設定が必要な場合、柔軟性に欠けていませんか。。。？


rubyでは設定ファイルをrubyのコードとして定義して、rubyインタープリンタに直接
解釈させる方法が良く採用される。railsのサーバー用設定もそのようになっているし、著名なruby-gemの設定ファイルは大抵そうなっている  

しかし、最も有名な例はVagrantで仮想マシンの設定を記述するためのVagrantfile。  
下の様にVagrantfileでは、配備する仮想マシンのOSの種類やメモリなどの情報をVagrantfileに記載する。  

**Vagrantfileの例**  
何の設定をしているのかが直観的にわかりやすい。

```ruby
Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "3024"
  end
end
```


Vagrantfileはrubyのプログラムとしてそのままrubyインタープリンタによって解釈される。  
Vagrantfileのような設定ファイルを作るためには```self yield```を用いる。  

**Vagrantfile風の設定を実現するモジュール**  

```ruby
module ExampleModule

  # この特異メソッドでは、設定情報を格納する為のクラスConfigを作成する。
  # 渡された変数とブロックを直接渡しておくだけ。
  class << self
    attr_reader :config
    def configure(name, &block)
      @config = Config.new(name, &block)
    end
  end

end

class ExampleModule::Config
  attr_accessor :name, :height, :width

  def initialize(name)
    self.name = name
    # yield self によってブロックが渡された時にブロック引数として
    # このインスタンス自身が渡される
    yield self if block_given?
  end

end
```

上記のExampleModule::configureでは単に設定を格納するためのクラスをインスタンス化し
、そこに与えられた引数とブロックをそのまま渡している。  
Config#initializeでは引数nameへの格納とyield selfを行っている。
yieldに引数が与えられた場合、その引数は与えられるブロックの引数になる。
このためこのメソッドにブロックが与えられると、
そのブロック引数はselfつまりConfig#initializeによってインスタンス化されるオブジェクト自身となる。
このため、ブロック内ではそのオブジェクトの変数を自由に設定できることになる。  

次のように形式でVagrantfile風の設定を行うことができる。

```ruby
ExampleModule.configure('test') do |config|
  config.height = 100
  config.width = 20
end

puts ExampleModule::config.name # => "test"
puts ExampleModule::config.height # => 100
puts ExampleModule::config.width # => 20
```

スペースやタブ、改行コード、パラメタ同士の
区切り文字を気にする必要がなく。Vagarantfileのようにパラメタの意味に従って
特定のパラメタに複数の値を設定させたり、ブロックで設定させたりができる。
（ただのrubyのメソッド呼び出しなので当然）  

rubyインタープリンタによって解釈されるため、以下のように変数を使った設定が
できるようになるところも利点

```ruby
ExampleModule.configure('test') do |config|
  width = 20
  config.height = width * 5
  config.width = width
end
```

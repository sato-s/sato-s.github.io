---
layout: post
title: ruby知らない人のためのイケてるrubygem5選
author: s sato 
tags:
- ruby
---


私がrubyを始めたきっかけはRuby on Railsでした。
数人（ときには1人）のチームで複雑なWebアプリケーションを短期で作れるという触れ込みだったので、Railsの勉強を始めました。
当時rubyはおろかhtml/cssさえもまともに書いたことはありませんでしたが、数カ月後にはRailsに関する噂は
嘘ではないことがわかりました。  

私がrubyを始めた理由は、Railsという強力なgem(ruby用のライブラリのことをそう言います)でした。しかし、Rails自体の開発者
にとってはどうだったでしょうか？  
Railsの登場以前のrubyはマイナー言語の部類で、特に著名なライブラリがあったわけでもありません。革新的なWebアプリケーションフレームワークを作ろうと思ったのであれば
rubyとよく比較される軽量プログラミング言語で使用者の多いpythonの方が、もっと妥当な選択肢に思われるかもしれません。
私はrubyを採用した最も大きな理由は、rubyの文法の美しさなのだと思います。
([実際にRailsの製作者のDHHことDavid Heinemeier Hansson氏はrubyを選んだ理由として美しさを挙げています](http://gihyo.jp/dev/serial/01/alpha-geek/0004))

私は、美しく書けるという特性がrubyと他の言語を分ける最も重要な特性なのではないかと思います。  
美しく書けるといってもとても伝わりずらいですが、実はvagrantのVagrantfleやchefのrecipeなどはただの設定ファイルではなく、とても美しく書かれた
rubyのソースコードそのものだったりするんです!

しかし、新しいプログラミング言語をやってみようという人に対するアピールとしては、みんな使ってるpython、すごい流行ってるGo、とにかく革新的なHaskellにくらべてよくわからないし伝わりずらいものです。

rubyをとにかくお勧めしたいが、文法の美しさという特性はは使って初めてわかるもので、ここに書いても納得してもらえるものではありません。
しかし、とにかく皆さんに使ってもらってほしいので、自分がRailsをきっかけにrubyを始めたように、rubyを知らない人が使ってみたいと思えるようなgemを紹介します。  

ここで紹介するgemはrubyをインストールすると入っているgemコマンドをたたくと、簡単にインストールできます。

```
gem install gemの名前
```

### [jekyll](https://jekyllrb-ja.github.io/)

jeykyllはmarkdownブログが簡単に作れるWebアプリケーションフレームワークです。  


```
jekyll new myblog
cd myblog
```

上のコマンドを実行すると、以下のようなディレクトリが作成されています。

```
├── about.md
├── _config.yml
├── Gemfile
├── Gemfile.lock
├── index.md
├── _posts # この中にマークダウンファイルを入れると記事になる。
│   └── 2016-12-13-welcome-to-jekyll.markdown
└── _site
```

jeykyll serveでサーバーを立ち上げるとローカルホストの４０００番でブログが立ち上がります。

```
jekyll serve --host=0.0.0.0 # サーバの立ち上げ。--hostを省略するとlocalからのみ参照可になる
```


    ---
    layout: post
    title:  "jeykyllで簡単ブログ記事"
    date:   2016-11-20 00:00:00 +0900
    categories: test
    ---

    ## コード

    ```ruby
    class Array
      def sum
        self.reduce(0,&:+)
      end
    end

    puts [1,2,3,4,5,5].sum
    ```

    ### テーブル

    |name|age|
    |---|---|
    |sato|29|
    |ito|12|



### [axlsx](https://github.com/randym/axlsx)

### [ruby-warrior](https://github.com/ryanb/ruby-warrior)

### [Reality](https://github.com/molybdenum-99/reality)

###



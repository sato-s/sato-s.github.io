---
layout: post
title: ruby知らない人にもおすすめ!イケてるrubygem4選
author: s sato 
tags:
- ruby
---


### はじめに

私がrubyを始めたきっかけはRuby on Railsでした。
当時rubyはおろかhtml/cssさえもまともに書いたことはありませんでしたが、数カ月後にはRailsの生産性すごい！と思えるようになりました。

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

というわけで、rubyやRailsを仕事で使う人以外も使ってみたくなるかもしれない、イケてるrubygemを紹介します。

ここで紹介するgemはrubyをインストールすると入っているgemコマンドをたたくと、簡単にインストールできます。

```
gem install gemの名前
```

### [jekyll](https://jekyllrb-ja.github.io/)

jeykyllはmarkdownブログが作れるWebアプリケーションフレームワークです。  
markdown形式なので、簡単に記事が書ける上に好きなjavascriptライブラリやjekyllプラグインを使ってカスタマイズできるのが特徴です。


```
jekyll new myblog
cd myblog
```

上のコマンドを実行すると、以下のようなディレクトリが作成されています。

```
myblog
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
cd myblog
jekyll serve --host=0.0.0.0 # サーバの立ち上げ。--hostを省略するとlocalからのみ参照可になる
```

結果

<img src="https://raw.githubusercontent.com/sato-s/sato-s.github.io/master/assets/jekyll-blog-top.JPG" alt="jekyll blog top exapmle" style="width: 500px;"/>


_postディレクトリ配下に、markdown形式で追加するだけでブログに記事を追加していくことができます。  

※ファイル名は2016-11-20-jekyll-test.mdのような感じで日付を先頭に書いておく必要があります

サンプル(myblog/_post/2016-11-20-jekyll-test.md)

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


結果

<img src="https://raw.githubusercontent.com/sato-s/sato-s.github.io/master/assets/jekyll-blog-artible.JPG" alt="jekyll article example" style="width: 500px;"/>

jekyllにはほかのフレームワークと一線を隔すもう一つの特徴がります。それは[githubがjekyllのホスティングをサポート](https://help.github.com/articles/about-github-pages-and-jekyll/)していることです。  
jekyllのディレクトリをgithubにpushするだけでgithubが勝手にホスティングをしてくれるんです！！！(これは楽ですね)  

なお、このブログもこの仕組みでホスティングされています。

### [axlsx](https://github.com/randym/axlsx)

ワークシートを追加する(```add_worksheet```)、行を追加する(```add_row```)などのメソッドで簡単にExcelが生成できます。  
報告書をExcelで書かないといけないけど、人力でExcelを書くのが面倒！という人におすすめ。  

サンプル

```
require 'axlsx'

Axlsx::Package.new do |p|
  p.workbook.add_worksheet(:name => "Example") do |sheet|
    sheet.add_row ['時','商品A','商品B','商品C','商品D']
    sheet.add_row ['今月',1,2,3,4]
    sheet.add_row ['先月',1,2,1,10]
  end
  p.serialize('example.xlsx')
end
```

結果

![axlsx example]({{ site.url }}assets/axlsx-example.JPG)

悪名高いExcel方眼紙も簡単！

```
require 'axlsx'

text = <<'EOS'
axlsxで簡単！
Excel方眼紙
EOS

Axlsx::Package.new do |p|
  p.workbook.add_worksheet(:name => "sheet1") do |sheet|
    text.each_line do |line|
      row = sheet.add_row 
      line.each_char{|char| row.add_cell char }
    end
  end
  p.serialize('hoganshi.xlsx')
end
```

結果

![excel-hoganshi]({{ site.url }}assets/excel-hogan.JPG)


ほかにも、グラフを作ったりセルの色やスタイルを変更できます。  
[公式のgithubのexample配下](https://github.com/randym/axlsx/tree/master/examples)を見るとやり方がわかります。

### [rubywarrior](https://github.com/ryanb/ruby-warrior)

RPG風の2dのマップ上を歩くAIが作れるgemです。  
道中の敵を攻撃したり、回避したり、危険な場合には休んで体力を回復したりしてゴールを目指すのが目的です。  

![ruby warrior](https://raw.githubusercontent.com/sato-s/sato-s.github.io/master/assets/ruby-warrior.gif)

- @ : プレイヤー
- s : 敵
- S : 強めの敵
- > : ゴール 

[上を動かしているコード](https://gist.github.com/sato-s/771b36fef877a5cec57dd321f7118105)

基本的な使い方は以下のように、```play_turn```メソッドの中で、```warrior```の様々なメソッドを呼び出して、プレイヤーの行動を決めていくことになります。  

```
class Player
  def play_turn(warrior)
		# warrior.feelで敵が存在するかを感知し、いればwarrior.attack!で攻撃。
    if warrior.feel.enemy?
      warrior.attack!
    #敵がいなければwarror.walkでそのまま進んでいく
    else
      warrior.walk!
    end
  end
end
```

このgemにインスパイアされた[webアプリ版rubywarrior](https://www.bloc.io/ruby-warrior/)も存在します。  
※注意　音が出ます。  

ゲームのAIに興味のある方に、ぜひおすすめ！

### [reality](https://github.com/molybdenum-99/reality)




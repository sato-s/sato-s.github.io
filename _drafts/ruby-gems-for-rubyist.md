# [ruby-warrior](https://github.com/ryanb/ruby-warrior)

# [Vimrunner]

# [curl-to-ruby](https://jhawthorn.github.io/curl-to-ruby/)

Gem zyanai!!


# [Reality](https://github.com/molybdenum-99/reality)



# [Haikunator](https://github.com/usmanbashir/haikunator)

HerokuやDockerがやっているように、覚えやすい名前を生成してくれる。  
ランダムな英数字で構成されたIDを使うのはやめよう。


```ruby
[1] pry(main)> require "haikunator"
=> true
[2] pry(main)> Haikunator.haikunate
=> "empty-wind-9025"
[3] pry(main)> Haikunator.haikunate
=> "young-wave-3996"
[4] pry(main)> Haikunator.haikunate
=> "nameless-star-8790"
[5] pry(main)> Haikunator.haikunate
=> "lively-smoke-3812"
```

# [annotate_gem](https://github.com/ivantsepp/annotate_gem)

Gemfileにコメントを付け加えてくれる。  
gemからインストールしてコマンドラインから使うこともできるが、webアプリも公開されている。

http://annotate-gem.herokuapp.com/

次のようなGemfileを入力すると

```ruby
gem "nokogiri"
gem "kaminari"
gem "hanami"
```

次のように変換してくれる。

```ruby
# Nokogiri (鋸) is an HTML, XML, SAX, and Reader parser (http://nokogiri.org)
gem "nokogiri"
# A pagination engine plugin for Rails 3+ and other modern frameworks (https://github.com/amatsuda/kaminari)
gem "kaminari"
# The web, with simplicity. (http://hanamirb.org)
gem "hanami"
```

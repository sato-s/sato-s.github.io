---
layout: post
title: rbenvをfishから使えるようにする。
author: s sato
tags:
- ruby
- linux
- fish
---

 [fish](http://fishshell.com/)はbashよりいろいろな面で使い勝手が良いが、exportが使えなかったり、heredocが使えなかったりとbashとの非互換が
 いろいろあって困る。  
 rbenvの導入も少し異なっていた。


#### rootユーザーからfish をインストール

```markup
sudo su -
curl http://fishshell.com/files/linux/RedHat_RHEL-5/fish.release:2.repo > /etc/yum.repos.d/shells:fish:release:2.repo
yum install fish -y
```

####  Shell を変更したいユーザーになってからシェルをfishに変更。

```markup
sudo su - user
chsh -s /usr/bin/fish
```


####  rbenvのインストール

```markup
sudo yum install git zlib zlib-devel openssl-devel ibxml2 libxml2-devel bzip2 gcc-c++ gcc make readline readline-devel -y;
git clone https://github.com/sstephenson/rbenv.git ~/.rbenv
git clone https://github.com/sstephenson/ruby-build.git ~/.rbenv/plugins/ruby-build
```


####  config.fishへのrbenv設定の追記

通常のbashの設定とは違うものを記載してやる必要がある。


```markup
echo '# rbenv
set PATH $HOME/.rbenv/bin $PATH
set PATH $HOME/.rbenv/shims $PATH
rbenv rehash >/dev/null ^&1' >> $HOME/.config/fish/config.fish
fish # 設定の再読み込み
```


####  あとは普通にインストール

```markup
rbenv install 2.3.1
rbenv global 2.3.1
ruby --version
```

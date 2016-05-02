---
layout: post
title: "CentOSにruby,rails,postgreSQLをインストールするために必要なパッケージ一覧"
date: '2016-05-02T18:16:00.001+09:00'
author: s sato
tags:
- Linux
---

CentOSにruby,rails,postgreSQLをインストールするまでに、以下のパッケージが必要だった。(いずれもソースからのインストール)  



```bash
sudo yum update -y;
sudo yum install wget zlib zlib-devel -y;

sudo yum install git -y;
sudo yum install readline bzip2 readline-devel gcc -y
sudo yum install -y openssl-devel;
sudo yum install -y libxml2 libxml2-devel;
sudo yum install  gcc-c++ patch -y;

# あるとよい
sudo yum install screen vim ctags -y;
```

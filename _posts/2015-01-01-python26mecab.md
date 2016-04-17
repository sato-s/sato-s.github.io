---
layout: post
title: Python2.6からMecab
date: '2015-01-01T17:55:00.002+09:00'
author: s sato
tags:
- 機械学習
- python
modified_time: '2015-01-01T17:55:49.546+09:00'
blogger_id: tag:blogger.com,1999:blog-1054230703994559763.post-4035083929859995148
blogger_orig_url: http://satomemocho.blogspot.com/2015/01/python26mecab.html
---


Mecab from python

rubyから使おうとしたときは苦労したし、python3から使おうとするとかなり面倒なようだが
python2.6(CentOS標準)からならかなり楽に使える。
Mecabが既にインストールされていることが前提

ダウンロード

```
wget https://mecab.googlecode.com/files/mecab-python-0.994.tar.gz
tar zxf mecab-python-0.994.tar.gz
cd mecab-python-0.994
su
python setup.py install
```

テストプログラム  
test.py

```
# coding: UTF-8
import sys
import MeCab
tagger = MeCab.Tagger ()
print tagger.parse ("吾輩は猫である")
```

結果

```
[sato@localhost python_training]$ python test.py 
吾輩  名詞,代名詞,一般,*,*,*,吾輩,ワガハイ,ワガハイ
は   助詞,係助詞,*,*,*,*,は,ハ,ワ
猫   名詞,一般,*,*,*,*,猫,ネコ,ネコ
で   助動詞,*,*,*,特殊・ダ,連用形,だ,デ,デ
ある  助動詞,*,*,*,五段・ラ行アル,基本形,ある,アル,アル
EOS
```
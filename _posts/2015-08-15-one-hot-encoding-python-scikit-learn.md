---
layout: post
title: one hot encoding (python scikit-learn)
date: '2015-08-15T18:31:00.001+09:00'
author: s sato
tags:
- 機械学習
- python
modified_time: '2015-08-15T18:32:42.828+09:00'
blogger_id: tag:blogger.com,1999:blog-1054230703994559763.post-4774073257860671181
blogger_orig_url: http://satomemocho.blogspot.com/2015/08/one-hot-encoding-python-scikit-learn.html
---

会員情報の職業や性別のようなカテゴリ値を用いて、機械学習をする際には、何らかの形で数値にする必要がある。 通常は、「会社員」や「学生」のようなカテゴリ情報は、取り得る値の種類と等しいサイズの配列のその値のみを1にした物を使う。 倒えば、会社員=[1,0]、学生=[0,1]のような形式になる。この表現形式をone-hot encodingまたは1 of K encodingと呼ぶ。
pythonのscikit-learnで以下のように、この変換ができる。 

次のような、accounts.csvがあると仮定する。

```
name,occupation
sato,adventurer
ito,engineer
inoue,student
tanaka,engineer
oda,adventurer
```


基本的にはDictVectorizerに入れるだけだが、その前に[(occupation=adventurer),(occupation=engineer)]のようなディクショナリの配列にする必要がある。

```python
# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.feature_extraction import DictVectorizer

accounts=pd.read_csv('./accounts.csv', encoding='utf-8')

occupation_vectorizer = DictVectorizer(sparse=False)

i = [ dict(occupation=occupation) for occupation in accounts[u"occupation"] ]

X = occupation_vectorizer.fit_transform(i)
names = occupation_vectorizer.get_feature_names()

# original table
print accounts
# label names
print names
# transformed one-hot encoding
print X
```


結果

```python
     name  occupation
0    sato  adventurer
1     ito    engineer
2   inoue     student
3  tanaka    engineer
4     oda  adventurer
[u'occupation=adventurer', u'occupation=engineer', u'occupation=student']
[[ 1.  0.  0.]
 [ 0.  1.  0.]
 [ 0.  0.  1.]
 [ 0.  1.  0.]
 [ 1.  0.  0.]]
 ```
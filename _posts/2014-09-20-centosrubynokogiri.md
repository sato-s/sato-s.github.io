---
layout: post
title: CentOSでrubyにnokogiri
date: '2014-09-20T19:56:00.002+09:00'
author: s sato
tags:
- ruby
modified_time: '2014-09-21T13:54:25.642+09:00'
blogger_id: tag:blogger.com,1999:blog-1054230703994559763.post-1057211623256471426
blogger_orig_url: http://satomemocho.blogspot.com/2014/09/centosrubynokogiri.html
---

普通にgem install nokogiriだといろんな依存ライブラリが足りない  
こんな感じで

```markup
yum install libxslt libxslt-devel libxml2 libxml2-devel -y
gem install nokogiri --use-system-libraries
```
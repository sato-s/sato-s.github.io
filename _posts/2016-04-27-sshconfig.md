---
layout: post
title: ".ssh/config"
date: '2016-04-27T01:04:00.001+09:00'
author: s sato
tags:
- Linux
---

.ssh/configの設定はこんな感じにすべきか  
上ですべてのマシン共通の設定をして、下でホストごとの設定をかく


```markup
### global setting ##
Host *
   User sato
   Port 22
   ServerAliveInterval 60
   StrictHostKeyChecking no
   IdentityFile ~/id_rsa

## per host setting ##
Host db1
  HostName 172.16.0.0
  User database
  IdentityFile ~/id_db
```

---
layout: post
title: python によるPID のロック
date: '2016-02-19T23:25:00.001+09:00'
author: s sato
tags:
- python
modified_time: '2016-02-19T23:25:37.524+09:00'
blogger_id: tag:blogger.com,1999:blog-1054230703994559763.post-8162933360753797094
blogger_orig_url: http://satomemocho.blogspot.com/2016/02/python-pid.html
---

pythonでpidを使った、多重実行の防止は以下のようにする。

```python
import time
import os
import sys

pid = str(os.getpid())
pidfile = "/tmp/scripy.pid"

if os.path.isfile(pidfile):
    print "exit"
    sys.exit(0)
file(pidfile, 'w').write(pid)
try:
    f = open('workfile', 'a')
    f.write("1")
    f.close
    time.sleep(10)

finally:
    os.unlink(pidfile)
```
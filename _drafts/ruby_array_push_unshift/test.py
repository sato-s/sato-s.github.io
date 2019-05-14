# push: 0:00:00.123131
# unshift: 0:05:31.523285

from datetime import datetime

a = []
t = datetime.now()
for _ in range(0, 1000000):
    a.append(1)
print("push: %s" % (datetime.now() - t))

a = []
t = datetime.now()
for _ in range(0, 1000000):
    a.insert(0, 1)
print("unshift: %s" % (datetime.now() - t))

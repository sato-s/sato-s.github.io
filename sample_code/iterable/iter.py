# -*- coding: utf-8 -*-

from functools import reduce
class Account:
    def __init__(self, age):
        self.age = age

    def is_child(self):
        return self.age < 20

class Accounts:
    def __init__(self):
        self._accounts = [Account(i) for i in range(10)]
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > len(self._accounts) - 1:
            raise StopIteration
        else:
            self.current += 1
            return self._accounts[self.current - 1]

# 初期化
accounts = [Account(age) for age in range(14, 30)]

# ここで、childrenはAccountsのインスタンスではなく、ただのAccountのlistになっている。
children = list(filter(lambda account : account.is_child(), accounts))
# このためAccountsに定義average_ageメソッドを定義しても使用できない
# 仕方ないので、ここで計算する。
average_age = reduce(lambda acc,account: acc + account.age, children, 0.0) / len(children)
print(average_age)

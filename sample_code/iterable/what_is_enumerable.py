# -*- coding: utf-8 -*-

from functools import reduce
class MyIntegers:
    def __init__(self, _integers):
        self._integers = _integers
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > len(self._integers) - 1:
            raise StopIteration
        else:
            self.current += 1
            return self._integers[self.current - 1]

integers = MyIntegers([1, 2, 3, 4, 5, 6, 7, 8 ,9, 10])

print(list(filter(lambda i: i % 2 == 0, integers))) # => [2, 4, 6, 8, 10]
integers.current = 0 # reset iterator
print(reduce(lambda i,acc: i + acc, integers, 0)) # => 55
integers.current = 0
print(reduce(lambda i,acc: i * acc, integers)) # => 3628800

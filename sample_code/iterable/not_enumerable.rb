
integers = [1, 2, 3, 4, 5, 6, 7, 8 ,9, 10]

p integers.select(&:even?) # => [2, 4, 6, 8, 10]
p integers.sum # => 55
p integers.reduce(&:*) # => 3628800

class MyIntegers
  include Enumerable

  def initialize(_integers)
    @_integers = _integers
  end

  def each
    @_integers.each{|i| yield i}
  end

end

integers = MyIntegers.new([1, 2, 3, 4, 5, 6, 7, 8 ,9, 10])

p integers.select(&:even?) # => [2, 4, 6, 8, 10]
p integers.sum # => 55
p integers.reduce(&:*) # => 3628800

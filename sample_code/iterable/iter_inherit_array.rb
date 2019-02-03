class Account
  attr_reader :age

  def initialize(age)
    @age = age
  end

  def child?
    @age < 20
  end

end

class Accounts < Array
  def initialize(*args)
    super(*args)
  end
end

accounts = Accounts.new([1,2,3,4,5])
require 'pry'
binding.pry

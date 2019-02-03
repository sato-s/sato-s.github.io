class Account
  attr_reader :age

  def initialize(age)
    @age = age
  end

  def child?
    @age < 20
  end

end

class Accounts
  include Enumerable

  def initialize(_accounts)
    @_accounts = _accounts
  end

  def each
    @_accounts.each{|account| yield account}
  end

  def select(*args, &block)
    self.class.new(@_accounts.select(*args, &block))
  end

end

children = accounts.select(&:child?)

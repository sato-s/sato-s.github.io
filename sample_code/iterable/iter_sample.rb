require 'json'

class Account
  attr_reader :id, :age

  def initialize(id, age)
    @id = id
    @age = age
  end

  def child?
    @age < 20
  end

  def to_tr
    <<~TR
      <tr>
        <td>#{@id}</td>
        <td>#{@age}</td>
      </tr>
    TR
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

  def average_age
    @_accounts.map(&:age).sum / @_accounts.size
  end

  def to_table
    <<~TABLE
      <table>
        <tr>
          <th>ID</th>
          <th>AGE</th>
        </tr>
        #{@_accounts.map(&:to_tr).join}
        <tr>
          <td>Average</td>
          <td>#{average_age}</td>
        </tr>
      </table>
    TABLE
  end

end

accounts = Accounts.new((1...5).map{|id| Account.new(id, rand(100))})

puts accounts.to_table

class Account
  attr_reader :id, :age

  def initialize(id, age)
    @id = id
    @age = age
  end

  def child?
    @age < 20
  end

end

module AccountsSelializer
  module_function
  def serialize(accounts)
    average_age = accounts.map(&:age).sum / accounts.size
    <<~TABLE
      <table>
        <tr>
          <th>ID</th>
          <th>AGE</th>
        </tr>
        #{accounts.map{|account| _account_to_tr(account)}.join}
        <tr>
          <td>Average</td>
          <td>#{average_age}</td>
        </tr>
      </table>
    TABLE
  end

  def _account_to_tr(account)
    <<~TR
      <tr>
        <td>#{account.id}</td>
        <td>#{account.age}</td>
      </tr>
    TR
  end
end

accounts = (1...5).map{|id| Account.new(id, rand(100))}
puts AccountsSelializer.serialize(accounts)

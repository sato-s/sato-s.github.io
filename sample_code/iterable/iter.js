class Account {
  constructor(age) {
    this.age = age
  }

  is_child() {
    return this.age < 20
  }
}

class Accounts extends Array {
  constructor(...args) {
    super(...args);
  }

  get average_age() {
    const sum = this.reduce((acc, account) => acc + account.age , 0)
    return sum / this.length
  }
}

// 初期化
let _accounts = []
for (let i = 14; i <= 29; i++){
  _accounts.push(new Account(i))
}
const accounts = new Accounts(..._accounts)

const children = accounts.filter((a) => a.is_child())
console.log(children.average_age)

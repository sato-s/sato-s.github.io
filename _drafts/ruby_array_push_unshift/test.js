// push: 0.042
// unshift: 251.464
//

var a = []
var t = Date.now()
for (let i = 0; i < 1000000; i ++){
  a.push(1)
}

console.log(`push: ${(Date.now() - t) / 1000}`)

var a = []
var t = Date.now()
for (let i = 0; i < 1000000; i ++){
  a.unshift(1)
}

console.log(`unshift: ${(Date.now() - t) / 1000}`)

# unshift: 0.088943619
# push: 0.083348431

a = []
t = Time.now
1_000_000.times{a.unshift(1)}
puts "unshift: #{Time.now - t}"

a = []
t = Time.now
1_000_000.times{a.push(1)}
puts "push: #{Time.now - t}"


Compile [Error](Error)

```
class Bar
  def print
    p "Bar"
  end
end

class Baz
end

bar = Bar.new
baz = Baz.new

foo = rand < 0.5 ? bar : baz
foo.print
```


Success

```
class Bar
  def print
    p "Bar"
  end
end

class Baz
  def print
    p "Bar"
  end
end

bar = Bar.new
baz = Baz.new

foo = rand < 0.5 ? bar : baz
foo.print
```

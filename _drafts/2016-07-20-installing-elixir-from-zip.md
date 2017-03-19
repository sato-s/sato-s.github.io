


rpm elixir which we can install with yum is so yesterday. (1.2)

download precompiled zip.

choose latest zip
https://github.com/elixir-lang/elixir/releases/


download and set path
```
wget https://github.com/elixir-lang/elixir/releases/download/v1.3.2/Precompiled.zip
mkdir elixir
unzip Precompiled.zip -d elixir
set PATH /home/sato/pkg/elixir/bin $PATH
set LD_LIBRARY_PATH /home/sato/pkg/elixir/lib $LD_LIBRARY_PATH
```

but invoking iex does not work due to the following error.


```Loading of ~ts failed elixir```


download latest erlang
http://www.erlang.org/downloads

and follow this instruction

https://docs.basho.com/riak/kv/2.1.4/setup/installing/source/erlang/#installing-on-rhel-centos

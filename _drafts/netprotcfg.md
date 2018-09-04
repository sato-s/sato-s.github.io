

### janssonのインストール



```
wget http://www.digip.org/jansson/releases/jansson-2.10.tar.gz
tar zxf jansson-2.10.tar.gz
cd jansson-2.10/
./configure
make 
sudo make install
```

### plotnetcfgのインストール

```
git clone https://github.com/jbenc/plotnetcfg.git
cd plotnetcfg
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig
make 
sudo make install
```



```
sudo plotnetcfg | dot -Tpng > test.png
```




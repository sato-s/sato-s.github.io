surge.sh
---------------------------------------

[surge.sh](https://surge.sh/)は、スタティックなサイトをホスティングしてくれるサービス  
すべてがコマンドラインで完結してくれて、とても手軽に使える。  

インストール  
```
npm install -g surge
```

適当にサイトを作る  
```
$ mkdir surge_test
$ cd surge_test/
$ echo '<h1>Hello World</h1>' > index.html
```


デプロイ  
```
$ surge

   Welcome to Surge! (surge.sh)
   Login (or create surge account) by entering email & password.

          email: s.sato.desu@gmail.com
       password:

   Running as s.sato.desu@gmail.com (Student)

            project: /home/sato/work/surge_test/
         domain: aspiring-show.surge.sh
         upload: [====================] 100% eta: 0.0s (1 files, 21 bytes)
            CDN: [====================] 100%
             IP: 45.55.110.124

   Success! - Published to aspiring-show.surge.sh
```


アカウント登録まですべてコマンドラインで完結するので、↑のコマンドだけで
http://aspiring-show.surge.sh/
にデプロイしてくれる。

## CIするとき

surgeのデプロイ時には、インタラクティブにユーザー名、パスワード、ドメイン名の入力を求められる。
CIするときには、これらは、コマンドラインの引数か環境変数にしたい。


このために、まずトークンを取得する。
```
$ surge token

  ***********************************
```

以下のように、引数を与えてやるとインタラクティブな入力なしにデプロイできる。
```
surge --token *********************************** --project ./ --domain aspiring-show.surge.sh
```

`--project`はindex.htmlの入っているディレクトリ名、`--domain`はデプロイ先のドメイン名

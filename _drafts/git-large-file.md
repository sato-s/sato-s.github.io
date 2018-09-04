gitでのバイナリファイルの管理
----------------------------------------


### git-lfsのインストール

```
➜  blob ls
git-lfs-linux-amd64-2.0.1.tar.gz
➜  blob tar zxf git-lfs-linux-amd64-2.0.1.tar.gz 
```

```
➜  blob cd git-lfs-2.0.1/

➜  git-lfs-2.0.1 sudo ./install.sh 
Git LFS initialized.
➜  git-lfs-2.0.1 
```

### 基本的な使い方

以下のようにバイナリファイルとして扱う拡張子を登録しておけば、あとは普通にpush/commitしてOKらしい。

```
git lfs track "*.jpg"
```

### 試してみる

最初に36kのファイルを用意

```
➜  lfs-test ls
test.jpg
➜  lfs-test du -h .
36K     .
➜  lfs-test 
```


リポジトリの初期化

```
➜  lfs-test git init
Initialized empty Git repository in /home/sato/Downloads/lfs-test/.git/
➜  lfs-test git:(master) ✗ git commit -a -m 'test'
On branch master
```


```
➜  lfs-test git:(master) ✗ du -h .
4.0K    ./.git/branches
44K     ./.git/hooks
8.0K    ./.git/info
8.0K    ./.git/objects/4b
4.0K    ./.git/objects/info
4.0K    ./.git/objects/pack
20K     ./.git/objects
4.0K    ./.git/refs/heads
4.0K    ./.git/refs/tags
12K     ./.git/refs
108K    ./.git
144K    .
```

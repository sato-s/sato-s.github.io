[インストール](http://knowledge.sakura.ad.jp/tech/1552/)

BIOSをいじって仮想化サポートをONにする必要があった。

```markup
mkdir ruby-gem-org
cd ruby-gem-org
```

```markup
vagrant init https://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-amd64-vagrant-disk1.box
```

```markup
vagrant up # VMの起動
vagrant ssh #  VMへ接続
vagrant halt # VMの停止
```

仮想マシン内の/vagrantディレクトリはVagrantfileが置かれているフォルダの場所と同期されている。

---
layout: post
title: kubernetes + distrolessはデバッグ可能か？
date: '2019-12-20T00:00:00.000+09:00'
author: s sato
tags:
- kubernetes
- linux
---


[distroless](https://github.com/GoogleContainerTools/distroless)は通常はインストールされているパッケージが
全く入っていない軽量なDockerイメージ。殆どなにも入っていないので、デプロイ／ビルドが高速で行えて
セキュリティ的にも堅牢な所からGoogleを含むいろいろなところで採用されている。  

だが個人的にはデバッグに対してかなり不安があった。netstat,tcpdump,ps,nslookup,ping...などのデバッグに必要な
コマンドが何1つ入っていないし,パッケージマネージャーも入っていないのであとからインストールするのも難しい。  
またシェルすら入っていないので、distrolessで作成されたPodに`kubectl exec`で乗り込む事もできない。  

```command
$ kubectl exec -it  testpod /bin/bash # bashが無いので当然無理
OCI runtime exec failed: exec failed: container_linux.go:348: starting container process caused "exec: \"/bin/bash\": stat /bin/bash: no such file or directory": unknown
command terminated with exit code 126
```

ログやメトリクスを適切に仕込んでおき、本番環境のPodに乗り込んでデバッグするような状況をなくすべきという主張はもっともだが、
個人的には何かあった時に備えてPodに入ってデバッグする手段は最低限確保しておきたい。  


### alpineやdistrolessのデバッグイメージを使う?

alpineはdistrolessと同じく必要なパッケージが殆ど何も入っていないDockerイメージだが、BusyBox
とパッケージマネージャーが入っている。同じくdistrolessにはデバッグイメージがよういされており
こちらもBusyBoxが入っている。  
1つの解決策としてdistrolessそのものを使わずにこういったイメージを使うことで、デバッグには困らずにすむだろう。
だがBusyBoxが入っていないdistrolessを使うことで、特にコマンドインジェクション系の脆弱性を防止できるのは
かなり利益が大きい気がした。セキュリティスキャンにひっかかってもほとんどの場合、誤検出だと胸をはって言えるはずだ。(そもそもコマンドが入ってない。)


### Ephemeral Containerを使う

Ephemeral Containerはkubernetesの機能で実行中のPodに一時的なコンテナを追加してデバッグするための仕組み。
一番妥当な解決策だが、かなり新しい機能でKubernetes 1.16からしか使うことは出来無い。(現時点でalpha機能)  
また、事前に[shareProcessNamespace](https://kubernetes.io/docs/tasks/configure-pod-container/share-process-namespace/)
が有効化され、コンテナ内のプロセスやファイルシステムがポッド内の他のコンテナと共有されていなければ、デバッグはできない。

### kubectl cpでBusyBoxを送ってデバッグ

[ここ](https://kazuhira-r.hatenablog.com/?page=1556456015)で紹介されていた方法で、dockerのコンテナにBusyBoxを送ってログインするというもの。  
Kubernetesで管理されたPodには`kubectl cp`でファイルを送信することが出来る。kubernetesでやろうとすると以下のようになる。  

```command
$ wget -q https://busybox.net/downloads/binaries/1.31.0-defconfig-multiarch-musl/busybox-x86_64
$ chmod 755 busybox-x86_64
$ kubectl cp busybox-x86_64 testpod:/usr/bin/busybox
$ kubectl exec -it  testpod /usr/bin/busybox ash
# => ashでログインできる
```

だが、上をdistrolessで作成されたコンテナに対して実行すると以下のように失敗してしまう。  

```command
$ kubectl cp busybox-x86_64 testpod:/tmp
OCI runtime exec failed: exec failed: container_linux.go:348: starting container process caused "exec: \"tar\": executable file not found in $PATH": unknown
error: Internal error occurred: error executing command in container: read unix @->/var/run/docker.sock: read: connection reset by peer
```

`kubectl cp`は現状tarが対象のコンテナ内に入っていないと動作しないらしい。
distrolessには勿論tarは入っていない。

[https://github.com/kubernetes/kubernetes/issues/58512](https://github.com/kubernetes/kubernetes/issues/58512)


### Node内からdocker cpでBusyBoxを送ってデバッグ 

`kubectl cp`がtarを必要とするのはdockerの制約ではなくkubernetesの制約のようだった。
distrolessの様なtarの入っていないイメージであっても`docker cp`の方は使用できるのでこっちを使えば同じことが出来る。
(dockerを使う必要があるので、kubernetesのNode内のdockerデーモンにアクセスできる必要はある)  
以下のような手順になる。  

コンテナのホストNodeを調べる

```command
$ kubectl describe pod testpod | grep 'Node:'
Node:               ******
```

コンテナのIDを調べる

```command
$ kubectl describe pod testpod | grep 'Container ID'
    Container ID:   docker://71d97aae302b98a8004f99a9757d43eed2d62991dd20053647cd1d1f3805d0a8
```

Node内からコンテナを参照してみる

```
$ sudo docker ps -f "id=71d97aae302b98a8004f99a9757d43eed2d62991dd20053647cd1d1f3805d0a8"
CONTAINER ID        IMAGE                       COMMAND                  CREATED             STATUS
71d97aae302b        kyos0109/nginx-distroless   "nginx -g 'daemon of…"   26 minutes ago      Up 26 minutes
```

Node内からbusyboxを転送する

```
wget -q https://busybox.net/downloads/binaries/1.31.0-defconfig-multiarch-musl/busybox-x86_64
chmod 755 busybox-x86_64
sudo docker cp busybox-x86_64 71d97aae302b98a8004f99a9757d43eed2d62991dd20053647cd1d1f3805d0a8:/usr/bin/busybox
```

あとはkubectlからPodないに入ることができる。  

```
kubectl exec -it  testpod /usr/bin/busybox ash
```

### まとめ

distrolessでも、本番のPod内に乗り込んでデバッグはできるので採用して良さそう。

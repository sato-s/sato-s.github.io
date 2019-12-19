---
layout: post
title: Kubernetes + distrolessはデバック可能か？
date: '2019-12-20T00:00:00.000+09:00'
author: s sato
tags:
- kubernetes
---


[distroless](https://github.com/GoogleContainerTools/distroless)はGoogleが公開している、通常はインストールされているパッケージが
全く入っていない軽量なDockerイメージ。軽量なのでデプロイ・ビルドが高速で
行え、セキュリティー


# Ephemeral Containers




# pod を作る

```
$ kubectl create -f test.yaml
```



```yaml
apiVersion: v1
kind: Pod
metadata:
  name: testpod
spec:
  containers:
    - name: test
      image: kyos0109/nginx-distroless
```

# /bin/bashできない

```
$ kubectl exec -it  testpod /bin/bash
OCI runtime exec failed: exec failed: container_linux.go:348: starting container process caused "exec: \"/bin/bash\": stat /bin/bash: no such file or directory": unknown
command terminated with exit code 126
```

# kubectl cpによる解決法

```
$ wget -q https://busybox.net/downloads/binaries/1.31.0-defconfig-multiarch-musl/busybox-x86_64
$ chmod 755 busybox-x86_64
$ kubectl cp busybox-x86_64 somepod:/usr/bin/busybox
Defaulting container name to print.
$ kubectl exec -it  somepod /usr/bin/busybox ash
# => ashでログインできる
```

kubectl cp は現状tarが必要  
https://github.com/kubernetes/kubernetes/issues/58512


```
$ kubectl cp busybox-x86_64 testpod:/tmp
OCI runtime exec failed: exec failed: container_linux.go:348: starting container process caused "exec: \"tar\": executable file not found in $PATH": unknown
error: Internal error occurred: error executing command in container: read unix @->/var/run/docker.sock: read: connection reset by peer
```

# node attach

コンテナのホストNodeを調べる

```
$ kubectl describe pod testpod | grep 'Node:'
Node:               ******
```

コンテナのIDを調べる


```
$ kubectl describe pod testpod | grep 'Container ID'
    Container ID:   docker://71d97aae302b98a8004f99a9757d43eed2d62991dd20053647cd1d1f3805d0a8
``

Nodeないからコンテナを参照してみる


```
$ sudo docker ps -f "id=71d97aae302b98a8004f99a9757d43eed2d62991dd20053647cd1d1f3805d0a8"
CONTAINER ID        IMAGE                       COMMAND                  CREATED             STATUS
71d97aae302b        kyos0109/nginx-distroless   "nginx -g 'daemon of…"   26 minutes ago      Up 26 minutes
```


Node内からbusyboxを転送

```
wget -q https://busybox.net/downloads/binaries/1.31.0-defconfig-multiarch-musl/busybox-x86_64
chmod 755 busybox-x86_64
sudo docker cp busybox-x86_64 71d97aae302b98a8004f99a9757d43eed2d62991dd20053647cd1d1f3805d0a8:/usr/bin/busybox
```

Nodeないからコンテナを参照してみる


```
kubectl exec -it  testpod /usr/bin/busybox ash
```

# まとめ

distrolessつかっててもデバックできるから採用しちゃって

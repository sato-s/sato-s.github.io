---
layout: post
title: １年使ってみてわかった。kubernetesのここがすごい
date: '2020-11-21T00:17:00.000+09:00'
author: s sato
tags:
- kubernetes
---

## tldr

- 宣言的設定とコントロールループ
- (凄まじく)高い拡張性
- 外部オブジェクトとkubernetesオブジェクトのマッピング
- 便利なkubernetesオブジェクト

## 背景

Heroku、AWS ECS、Azure Web AppのようなPaaSはアプリケーションエンジニアにとって、インフラのことを意識することのない
完璧なサービスに見える。なぜ世間はわざわざ高いインフラ管理と学習のコストを払ってk8sに移行しているんだろうか。   
アプリケーションエンジニアとして１年ほどk8sに携わり、やっと世間がk8sを祭り上げる理由がわかってきた気がするので、その理由について書いてみる。


## やってみよう

実はkubernetesを使ってみるのは、とても簡単。
[minikube](https://kubernetes.io/ja/docs/tasks/tools/install-minikube/)は簡単に動かせるkubernetesクラスター。単一のバイナリで構成され、MacやWindowでも動作する。(以下はMac用)

```
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64 \
  && chmod +x minikube
sudo mv minikube /usr/local/bin
minikube start
```

(本物のk8sで試してみたい方には、Digital Oceanや、Azureの無料枠が安くておすすめ)


kubectlコマンドでnode(dockerコンテナの入るホストマシン)の状態を見てみる。
(手元のマシンだけがk8sクラスターに組み込まれているので１つだけになるはず。)

```
$ kubectl get node
NAME       STATUS   ROLES    AGE     VERSION
minikube   Ready    master   2m59s   v1.19.4
```

ここまでできてれば、もうk8sにアプリケーションをデプロイすることができる  
こんな感じで、deployment.yamlを定義してデプロイしてみよう！

```
$ cat << EOF > deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
EOF

$ kubectl apply -f deployment.yaml
```

```
$ kubectl get pod
NAME                                READY   STATUS              RESTARTS   AGE
nginx-deployment-66b6c48dd5-cxgq8   0/1     ContainerCreating   0          20s
nginx-deployment-66b6c48dd5-dz7mr   0/1     ContainerCreating   0          20s
nginx-deployment-66b6c48dd5-qrq2h   0/1     ContainerCreating   0          20s
```

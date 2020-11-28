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
- sidecar

## 背景

Heroku、AWS ECS、Azure Web AppのようなPaaSはアプリケーションエンジニアにとって、インフラのことを意識することのない
完璧なサービスに見える。なぜ世間はわざわざ高いインフラ管理と学習のコストを払ってk8sに移行しているんだろうか。   
アプリケーションエンジニアとして１年ほどk8sに携わり、やっと世間がk8sを祭り上げる理由がわかってきた気がするので、k8s知らん勢に向けて、その理由について書いてみるよー

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
こんな感じで、deployment.yamlを定義してnginxをデプロイしてみよう！

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
        image: nginx:1.18.0-alpine
        ports:
        - containerPort: 80
EOF

$ kubectl apply -f deployment.yaml
```

このdeployment.yamlは、簡単に言うとどのようなPod(コンテナの集まり)を何個つくるかをきめるDeploymentというものの設定だ。
以下からわかるように、このDeploymentはPodを３つ作るものになる。

```yaml
spec:
  replicas: 3
```

その下の部分ではPodに入るコンテナが宣言されていて、今回の場合は 1.18.0-alpine になっている。

```yaml
    spec:
      containers:
      - name: nginx
        image: nginx:1.18.0-alpine
        ports:
        - containerPort: 80
```

このコマンドが終わったら、下のコマンドで、このDeploymentの状態を確認してみよう

```
$ kubectl get deployment
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
nginx-deployment   3/3     3            3           5d9h
```

READYが3/3ということは、３つのPodすべてが動いているということになる。Podの状態を見てみよう。

```
$ kubectl get pod
nginx-deployment-66b6c48dd5-cxgq8   1/1     Running   1          5d9h
nginx-deployment-66b6c48dd5-dz7mr   1/1     Running   1          5d9h
nginx-deployment-66b6c48dd5-qrq2h   1/1     Running   1          5d9h
```

生きているのが確認できたなら、実際にアクセスしてみよう。以下のコマンドで、localhost:8080への通信を今作ったDeploymentの80番ポート(nginxが動いてる)
にフォワードすることができる。

```
$ kubectl port-forward deployment/nginx-deployment 8080:80
```

localhost:8080を参照してみるとnginxが動いていることがわかるはず。

![nginx-welcome]({{ site.url }}/assets/nginx.png)


## 宣言的設定とコントロールループ

Deploymentはk8sでアプリケーションを管理するために利用される基本的なオブジェクトでおもに
①どんなPodがほしいか②何個ほしいかを宣言するものになっている。  
これが崩れたときに何が起こるかを見てみよう。  
いま、下のようなDeploymentによって３つのPodが作成されている。

```
$ kubectl get deployment
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
nginx-deployment   3/3     3            3           5s

$ kubectl get pod
NAME                               READY   STATUS    RESTARTS   AGE
nginx-deployment-5cb95ccc7-6hl8g   1/1     Running   0          5s
nginx-deployment-5cb95ccc7-6vk6m   1/1     Running   0          5s
nginx-deployment-5cb95ccc7-rxgj9   1/1     Running   0          5s
```

このPodの中の１つを削除してみよう。

```
$ kubectl delete pod nginx-deployment-5cb95ccc7-6vk6m
```

そうすると、削除したPodは、Terminating状態になる、とほぼ同時に、新しいPodが立ち上がりはじめる。
(AGEが１つだけ、8sのがあるので新しいPodができたことがわかる。)

```
$ kubectl get pod
NAME                               READY   STATUS        RESTARTS   AGE
nginx-deployment-5cb95ccc7-6hl8g   1/1     Running       0          20s
nginx-deployment-5cb95ccc7-6vk6m   0/1     Terminating   0          20s
nginx-deployment-5cb95ccc7-rxgj9   1/1     Running       0          20s
nginx-deployment-5cb95ccc7-z4wbf   1/1     Running       0          8s
```

もうしばらくすると、Terminating状態のPodはなくなり、Podの数は３つになる。

```
$ kubectl get pod
NAME                               READY   STATUS    RESTARTS   AGE
nginx-deployment-5cb95ccc7-6hl8g   1/1     Running   0          34s
nginx-deployment-5cb95ccc7-rxgj9   1/1     Running   0          34s
nginx-deployment-5cb95ccc7-z4wbf   1/1     Running   0          22s
```


```yaml
spec:
  replicas: 3
```
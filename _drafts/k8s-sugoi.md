---
layout: post
title: １年使ってみてわかった。kubernetesのここがすごい
date: '2020-11-21T00:17:00.000+09:00'
author: s sato
tags:
- kubernetes
---

## 背景

アプリケーションエンジニアとして新規立ち上げのプロジェクトで１年ほどk8sに携わってきた。
知識ゼロのところからだったので、はじめは戸惑うことばかりだったが、なれるうちにk8sはインフラの未来だ、googleすげーと思うようになってきた。
Heroku、AWS ECS、Azure Web AppのようなPaaSはアプリケーションエンジニアにとって、インフラのことを意識することのない
完璧なサービスに見える。なぜ世間はわざわざ高いインフラ管理と学習のコストを払ってk8sに移行しているんだろうか。   

やっと世間がk8sを祭り上げる理由がわかってきた気がするので、k8s知らん勢に向けて、その理由について書いてみるよー

## tldr

- 宣言的設定とコントロールループ
- (凄まじく)高い拡張性
- 外部オブジェクトとkubernetesオブジェクトのマッピング

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

Deploymentはk8sでアプリケーションを管理するために利用される基本的なオブジェクトで、おもに
①どんなPodがほしいか②何個ほしいかを宣言するものになっている。  
さっき作成したのとおなじdeployment.yamlをつかって、これが崩れたときに何が起こるかを見てみよう。  
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
nginx-deployment-5cb95ccc7-6vk6m   0/1     Terminating   0          20s ★消されているPod
nginx-deployment-5cb95ccc7-rxgj9   1/1     Running       0          20s
nginx-deployment-5cb95ccc7-z4wbf   1/1     Running       0          8s  ★新しいPod
```

もうしばらくすると、Terminating状態のPodはなくなり、Podの数は３つになる。

```
$ kubectl get pod
NAME                               READY   STATUS    RESTARTS   AGE
nginx-deployment-5cb95ccc7-6hl8g   1/1     Running   0          34s
nginx-deployment-5cb95ccc7-rxgj9   1/1     Running   0          34s
nginx-deployment-5cb95ccc7-z4wbf   1/1     Running   0          22s    ★新しいPod
```

deployment.yamlで下のように、Podの数(レプリカ)を３つと宣言しているので、Deploymentは
それを保つためにPodが削除された時に、新しいPodを作り直してくれた。

```yaml
spec:
  replicas: 3
```

今度は、逆にDeploymentのreplicasの数を5に変えてみよう。Deploymentの定義は以下のようにkubectl editを使うとエディタで編集することができる。

![edit-replicas]({{ site.url }}/assets/k8s_deployment_edit_replicas.gif)

しばらくして、参照するとPodの数は５つに増えている。

```
$ kubectl get pod
NAME                               READY   STATUS    RESTARTS   AGE
nginx-deployment-5cb95ccc7-6hl8g   1/1     Running   0          89m
nginx-deployment-5cb95ccc7-dd8dc   1/1     Running   0          57s
nginx-deployment-5cb95ccc7-rp55x   1/1     Running   0          57s
nginx-deployment-5cb95ccc7-rxgj9   1/1     Running   0          89m
nginx-deployment-5cb95ccc7-z4wbf   1/1     Running   0          89m
```

もう少し別な変更の仕方をしてみよう。今度はreplicasの数を5から１に変更し、同時に
使用するイメージを nginx:1.18.0-alpine から nginx:1.19.5-alpine に変更してみる。

![edit-version]({{ site.url }}/assets/k8s_deployment_edit_version.gif)

すると、5つのPodの内の４つがTerminating状態になり、あたらしく１つのPodが作られ始める。

```
$ kubectl get pod
NAME                               READY   STATUS              RESTARTS   AGE
nginx-deployment-5cb95ccc7-6hl8g   1/1     Running             0          113m
nginx-deployment-5cb95ccc7-b8qtj   0/1     Terminating         0          2m48s
nginx-deployment-5cb95ccc7-psmk7   0/1     Terminating         0          2m48s
nginx-deployment-5cb95ccc7-t8t7f   0/1     Terminating         0          2m48s
nginx-deployment-5cb95ccc7-wz7s9   0/1     Terminating         0          2m48s
nginx-deployment-8dbdfb87c-r8dqt   0/1     ContainerCreating   0          8s      ★新しく作られているPod
```

最終的には、Podは１つだけになる。

```
$ kubectl get pod
NAME                               READY   STATUS    RESTARTS   AGE
nginx-deployment-8dbdfb87c-r8dqt   1/1     Running   0          26s
```

このPodのイメージを参照してみると nginx:1.19.5-alpine になっている。
```
$ kubectl get pod nginx-deployment-8dbdfb87c-r8dqt -o yaml
# (kubectl get に -o yaml オプションをつけるとk8s上のPodの全定義がyaml形式で見れる)

# 略
spec:
  containers:
  - image: nginx:1.19.5-alpine
    imagePullPolicy: IfNotPresent
    name: nginx
    ports:
# 略
```

このDeploymentの例では、Podが削除された時に、新たに足りないPodが立ち上がり、逆にDeploymentが修正された時には、
それに合わせた、数、イメージのPodが立ち上がった。
Deploymentは望ましい状態(Podの数、イメージのバージョン) を宣言するためのオブジェクトで、現在の状態が
そこからずれてしまった場合には、k8sは自動的にそのズレを修正してくれるようになっている。
このように、現在の状態を望ましい状態に近づけてくれるためのk8sの仕組みはコントロールループ(Reconciliationループとも)と呼ばれている。  
(制御工学っぽい)  

![control loop]({{ site.url }}/assets/2880px-Feedback_loop_with_descriptions.svg.png)

*[wikipedia](https://en.wikipedia.org/wiki/Control_theory) より*

PodやDeploymentだけでなくk8sの他のオブジェクトも、基本的にこのコントロールループによって実現されている。
例えば、[Horizontal Pod Autoscaler(HPA)](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
は、負荷に合わせたPodのスケールアウトを実現するためのオブジェクトで下の様に対象のDeploymentと平均CPU使用率のしきい値(`averageUtilization`)を記載することができる。

```yaml
# 略
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: [デプロイメントの名前]
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
```

HPAは、特定のDeploymentに所属するPodの平均CPU使用率を監視し、それが特定の値を超えた場合、
Deploymentで以下の様に宣言していたreplicasの値を書き換える。

```yaml
spec:
  replicas: 3
```

そうするとDeploymentはPodの数を増やすので、結果としてPodの平均CPU使用率が下がるという仕掛けだ。

現実のWebアプリケーションでは、マシンの障害でPodがいきなり消えたり、負荷の増大でスケールアウトが必要になったり、
バグの修正のため新しいバージョンをリリースしたりする必要がある。こういったときは、上でPodを削除したり、replicasを増やしたり、imageをアップデートしたのと同じ
ことをしなければならない。
k8sでは、それぞれの要件に対して別々の機構を持っているわけではなく、全てこのコントロールループの作用によって対応される。(すごい！すごくない？)

## (凄まじく)高い拡張性 

k8sはコンテナをホスティングするためのプラットフォームだ。PodやDeploymentは、その基本となるオブジェクトでAWSでいうとEC2に相当するものだ。
しかし、AWSでいう、RDS,ELB,Elastic Cache,S3....のようなサービスはk8sには入っていない。
なぜかというと、そのようなサービスはk8s自体のソースコードを変更することなく自由に付け足すことができるためだ。    

これを実現するためのオブジェクトがCustomResourceDefinition(CRD)だ。CRDはその名の通りユーザーが
カスタムしたオブジェクトをk8s上に定義するためのオブジェクトだ。   
以下のような、crd.yamlを用いることで、k8s上にHogeという種類のオブジェクトを定義できるようになる。

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: hoges.stable.example.com
spec:
  group: stable.example.com
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                fuga:
                  type: string
  scope: Namespaced
  names:
    plural: hoges
    singular: hoge
    kind: Hoge
    shortNames:
      - hg
```

以下のように適用することができる。

```
$ kubectl apply -f crd.yaml
```

例えば、以下のような hoge.yaml を作成すれば、上記と同様に`kubectl apply -f hoge.yaml`でこのHogeという種類の
オブジェクトを作成することができる。(`kind: Hoge` のオブジェクトになっている)

```yaml
apiVersion: stable.example.com/v1
kind: Hoge
metadata:
  name: test-hoge
spec:
  fuga: hugahuga
```

定義したHogeのオブジェクトはPodやDeploymentと同様に`kubectl get`で参照することができる。

```
$ kubectl get hoge
NAME        AGE
test-hoge   80s
```

ここだけであれば、ただのカスタムしたオブジェクトが見れるだけで、なんの意味もない。
しかし、このオブジェクトに対応するコントロールループが実装できたらどうだろうか？
実はk8sではコントロールループを実装したPodをクラスタ上にデプロイすることで、これが実現できてしまう。
コントロールループ内で、CRDを参照し、その定義に従ってk8s内の他のオブジェクトを作ったり消したり設定
変更することによって、好みのオブジェクトを作ることができる。  
例えば、databaseという名前のCRDを作って、その定義に従ってPostgreSQLやMYSQLのイメージからPodを作り出す
コントロールループを実装すれば、AWSでいうRDS相当の機能が実現できてしまう。
このようなCRDに対するコントロールループは特にOperatorと呼ばれ、CRDとOperatorを作って、k8sを拡張することは
[Operator pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)
と呼ばれている。
いろんなk8sのOperatorが作られていて、例えば以下のようなものがあるよ。   

- [zalando/postgres-operator](https://github.com/zalando/postgres-operator)
はその名の通りPostgreSQLを作ってくれるオペレーターで、AWSで言うところのRDSに相当するものになる。
レプリケーション、バックアップ、ポイントインタイムリカバリ、コネクションプーリングなどなどのデータベースサービスに期待される
機能が一通り揃っている。
- [knative](https://knative.dev/)
はFaaS(Function as a service)を実現するオペレーターでAWSで言うところのLambdaだ。リクエストが来るとPodを立ち上げて
それをさばき、暇な時はPodを落としてくれる。アプリケーションによってはリソース効率を大きく上げることができる。
- [Istio](https://istio.io/)
はマイクロサービス用のサービスメッシュの代表格で、これもOperatorを使って実現されている。

他にもいろんなOperatorが[OperatorHub](https://operatorhub.io/)
で公開されている。

もちろん、このような仕組みは[kubebuilder](https://github.com/kubernetes-sigs/kubebuilder)
などのフレームワークを使うことで自分で実装することができる。
(自分もatコマンド相当のOperatorを作ったことがあるので良かったら[過去記事](http://sato-s.github.io/2020/03/20/k8s-at.html)
を読んでね。)   

このようなコントロールループを利用したOperatorのエコシステムがあり、便利なものが作られ続けることがk8sの利点の一つだ。

## 外部オブジェクトとkubernetesオブジェクトのマッピング


> Kubernetes (K8s)は、デプロイやスケーリングを自動化したり、コンテナ化されたアプリケーションを管理したりするための、オープンソースのシステムです。

*[公式サイトより](https://kubernetes.io/ja/)*

公式サイトの謳い文句の通りk8sはコンテナを管理するためのものだ。
だが、現実的なWebアプリケーションはコンテナを作るだけでは実現できない。
静的ファイルを高速に世界各地に届けるためにはS3やCDNを使う必要があるし、
大量のデータを扱うためにはDynamodbのようなほぼ際限なくスケールしてくれるKVSを使いたい。
k8s上にデータベースを作るためには、そもそもコンテナが消えてもデータが残るストレージが必要になるし、あるいはk8s上にデータベース
を作るのではなく、RDSを使うのが良いのかもしれない。   

このようなk8sの外のオブジェクトも、実は先程まで紹介していたOperatorを使うことでk8s上のオブジェクトとして扱うことができる。
例えば、アプリケーションがファイルをアップロードするためのS3のバケットが必要な場合、S3というCRDとそれを参照して
実際にAWS上にS3のバケットを作成するコントロールループを実装すれば良い。
このようなオペレータもいろんなものが実装されており、例えば以下のようなものがある。  

- [Azure Service Operator](https://github.com/Azure/azure-service-operator)
はAzure公式ののいろいろなサービスを作ってくれるOperator。[過去記事](http://sato-s.github.io/2020/08/26/azure-service-operator.html)
でAzure Postgresをつかってみてるよ。
- [AWS Controllers for Kubernetes](https://github.com/aws/aws-controllers-k8s)
はAWSが作っているAWSのサービスを作ってくれるOperator。まだdeveloper preview。
- [Crossplane](https://crossplane.io/)
はAWS,GCP,Azureを含むいろんなクラウド上のリソースを定義してくれるオペレーター

このようなCRDを作っておくことで、AWSコンソールやTeraformでAWS上の設定をして、その情報をk8sの定義に
記載するといった作業がなくなり、k8sの定義のみで必要な設定のすべてを記述することができる。   
(Infrastructure as Codeの完成形だ！)

## まとめ

k8sはコントロールループとそれを拡張可能にするというとても賢い仕組みがあり、
必要なサービスを作ったり外部のオブジェクトをk8s上のオブジェクトとして扱うことができるようになっている。
この拡張はさまざまなところで開発されていて、エコシステムは今後も大きくなりk8sはより便利になっていくと思う。
この辺が他のコンテナ管理用のプラットフォームやPaaSではなくk8sを使う理由になると思う。

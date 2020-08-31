---
layout: post
title: Azure Service Operatorがすごい
date: '2020-08-27T00:00:00.000+09:00'
author: s sato 
tags:
- kubernetes
- azure
---

１年ほどAWS EKSのkubernetesクラスター上のアプリを開発、運用する仕事を続けてきたが、
kubernetesの運用に関する最も大きな不満はほかのAWSのマネージドサービスとの連携部分だった。  

> Kubernetesを使うとデプロイしたコンテナのあるべき状態を記述することができ、制御されたスピードで実際の状態をあるべき状態に変更することができます。
([kubernetesドキュメント](https://kubernetes.io/ja/docs/concepts/overview/what-is-kubernetes/)より) 

公式ドキュメントに上のようにある通りkubernetesでは、あるべき状態を(おもにyamlで)定義すると、それを自動で作り出してくれる。  

例えば、下のようなyamlは、[nginxのイメージ](https://hub.docker.com/_/nginx)からコンテナを３つ作成してくれる。

```yaml
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
        image: nginx:latest
        ports:
        - containerPort: 80
```

このようなyamlでkubernetes上の資産を管理できることは、以下のようなメリットがある。

- 資産構成をどの開発者にも明白な形でドキュメントに残せる  
- 設計書(yaml)と実体がずれることがない   
- 設計書(yaml)がバージョンコントロールされる   
- 資産構成の変更=yamlの変更なので、どの開発者にも容易でしかも履歴に残る   
- **要はInfrastructure as Codeができる**   

だが、自分が所属していたプロジェクトでは実際には、そこまでうまく運用することはできなかった。
なぜなら、実際の"あるべき状態"はkubernetesの外部に依存するためだ。  

現実的なwebアプリケーションはRDB、メッセージキューなどの外部のサービスに依存する場合がほとんどだ。
このプロジェクトでも、RDSやSQS、S3などのAWSのマネージドサービスを使用していた。

```yaml
# 略
spec:
  containers:
  - name: server
    image: server:latest
    env:
    - name: DB_HOST
      value: "db.example.com"
    - name: DB_PORT
      value: "5432"
    - name: DB_NAME
      value: "app"
    - name: DB_PASSWORD
      value: "password"
```

このような場合、その接続のための情報を上のように環境変数としてyamlに定義する必要がある。
例えば、RDBとDynamoDBとS3を利用するWebアプリを作りたい場合、kubernetes用のyaml
を書く前に、AWS上でRDSのインスタンスとそのユーザーやDB、DynamoDBのテーブル、
S3のバケットなどの作成を済ませ、yamlにはそれらの情報を環境変数として記載しなければならない。
(実際にはConfigMapやSecretに記載するかも)   


これがInfrastructure as Codeへの大きな足かせになった。Podの定義をyamlとして一貫した形で
コードにできても、結局それが依存するAWSのマネージドサービスの定義はAWSのコンソールから
直接作ったりCloud formationで作成しなければならない。
これでは、kubernetes用のyamlを見てもインフラ構成全体を把握することもできないし、
変更するのにもkubernetesとAWSの両方の領域を意識して行う必要がある。
さらに悪いことに、自分の所属していたプロジェクトでは、AWS側とkubernetesで管理するチームが分かれていたので
資産構成の変更は複数のチームで協調しながら行わなければならなかった。
(AWSチームに頼んで作ってもらったＤＢをkubernetesチームがyamlに書いたりする)　


## マネージドサービスを使うのをやめる？

１つの選択肢として、今まで使用していたRDSやSQS、S3などのマネージドサービスをやめ、
kubernetes上にRDB、メッセージキュー、オブジェクトストレージなどを構築してしまうこともできる。
だが、いままでマネージドサービスが担保してくれていた高可用性、オートスケーリング、バックアップ、
ポイントインタイムリカバリなどなどの機能を自前で用意することになる。
しかも、さらに難しいことに、これらをコンテナ上で行わなければならない。
PostgreSQLのようなメジャーなものであれば、
マネージドサービス相当の機能性を実現するkubernetesの[Operator](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)
が存在しているが、結局のところ今までAWSが担保してくれていたものを自前で担保しなければ
ならなくなることに変わりはない。  

特にデータベースをkubernetes上に構築することに関しては
[Google Cloudのブログ](https://cloud.google.com/blog/products/databases/to-run-or-not-to-run-a-database-on-kubernetes-what-to-consider)
でも、現状課題が多いことが言及されている。

> While running a database in Kubernetes is gaining traction, it is still far from an exact science.

## Azure Service Operator

[Azure Service Operator](https://github.com/Azure/azure-service-operator)はマイクロソフトが
最近(2020/6)にリリースしたkubernetesの
[Operator](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)
でkubernetes上に定義したリソースの通りに、Azure上のマネージドサービスを作成、設定してくれるものだ。
これを使えば、kubernetesのyamlですべての資産構成を管理しつつマネージドサービスの恩恵も受けることができる。

### 使いかた

まずはAzure Service Operatorを使うには[手順](https://github.com/Azure/azure-service-operator#quickstart)
に従って、kubernetesクラスタにインストールする必要がある  

kubernetesは`kubectl api-resources`でkubernetes上のオブジェクトの一覧を参照できるので
、これでAzure Service Operatorでインストールされた資産も参照することができる。

```bash
$ kubectl api-resources | grep 'azure.microsoft.com'
 apimgmtapis                       apim         azure.microsoft.com            true         APIMgmtAPI
 apimservices                      apims        azure.microsoft.com            true         ApimService
 appinsights                       ai           azure.microsoft.com            true         AppInsights
 appinsightsapikeys                             azure.microsoft.com            true         AppInsightsApiKey
 azureloadbalancers                alb          azure.microsoft.com            true         AzureLoadBalancer
 azurenetworkinterfaces            ani          azure.microsoft.com            true         AzureNetworkInterface
 azurepublicipaddresses            apipa        azure.microsoft.com            true         AzurePublicIPAddress
 azuresqlactions                   asqla        azure.microsoft.com            true         AzureSqlAction
 azuresqldatabases                 asqldb       azure.microsoft.com            true         AzureSqlDatabase
--- 略 ---
```

現状、Azure Database(RDS相当)、Storage Account(S3相当)、Cosmos DB(DynamoDB相当)などなどのマネージドサービスに対応している。
各リソースの使い方は[github](https://github.com/Azure/azure-service-operator)にサンプルが載っている。  

### postgresqlserversサーバーを作成してみる

Azure Service Operatorで管理可能なリソースのうちpostgresqlservers(psqls)を使ってみる。

```
postgresqlservers                 psqls        azure.microsoft.com            true         PostgreSQLServer
```

上記は、以下のようなyamlを`kubectl apply -f`で適用することで作成できる。

```yaml
apiVersion: azure.microsoft.com/v1alpha1
kind: PostgreSQLServer
metadata:
  name: azure-operator-test-1231 # ユニークな名前にする必要がある
spec:
  resourceGroup: test
  location: japaneast
  serverVersion: "10"
  sslEnforcement: Enabled
  sku:
    name: B_Gen5_1
    tier: Basic
    family: Gen5
    size: "1000"
    capacity: 1
```

しばらくするとAzure側で上記に対応したAzure Postgresが作成される。

```
$ az postgres server list 
[
  {
		// 略
    "name": "azure-operator-test-1231",
    "sku": {
      "capacity": 1,
      "family": "Gen5",
      "name": "B_Gen5_1",
      "size": null,
      "tier": "Basic"
    },
    "version": "10"
		// 略
  }
]
```

対応するマネージドサービスがAzureで作成されると、kubernetes側で以下のようにこのPostgreSQLのサーバーが`successfully provisioned`になる。

```
$ kubectl get psqls azure-operator-test-1231
NAME                       PROVISIONED   MESSAGE
azure-operator-test-1231   true          successfully provisioned
```

このとき、同時に同じ名前でSecretが作成される。

```
$ kubectl describe secret azure-operator-test-1231
Name:         azure-operator-test-1231
Namespace:    default
Labels:       <none>
Annotations:  <none>

Type:  Opaque

Data
====
fullyQualifiedUsername:    33 bytes
password:                  16 bytes
postgreSqlServerName:      24 bytes
username:                  8 bytes
fullyQualifiedServerName:  52 bytes
```

このSecretのキー名を見るとわかる通りDBへの接続情報がこのSecretに入っている。
例えば、サーバーのホストは`fullyQualifiedServerName`を参照すればよい。


### postgresqlserversを利用したWebアプリを作ってみる

kubernetes上でpostgresqlserversを作成すると、それに対応した同名のSecret内にDBの接続のための
パスワードやホスト名のような情報が格納される。
このためWebアプリを作りたい場合には以下のようにyaml上で、Postgresサーバーに対応する
Secretの必要なキーをWebアプリのdeploymentの環境変数に入れることで、Webアプリ側で作成したPostgresサーバーを
使えるようにできる。
(あるいはSecretをマウントしてもよい)

```yaml
# Postgresサーバー
apiVersion: azure.microsoft.com/v1alpha1
kind: PostgreSQLServer
metadata:
  name: azure-operator-test-1233
spec:
  resourceGroup: test
  location: japaneast
  serverVersion: "10"
  sslEnforcement: Enabled
  sku:
    name: B_Gen5_1
    tier: Basic
    family: Gen5
    size: "1000"
    capacity: 1
---
# Webアプリ
apiVersion: azure.microsoft.com/v1alpha1
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
        image: nginx:latest
        env:
          # ここで、PostgreSQLServerに対応するSecret内の
          # DB接続情報を環境変数に入れる。
          - name: DB_HOST # ホスト
            valueFrom:
              secretKeyRef:
                # nameはSecretの名前
                # これはPostgreSQLServerのmetadata.nameと同じになる
                name: azure-operator-test-1233
                key: postgreSqlServerName
          - name: DB_PASSWORD # パスワード
            valueFrom:
              secretKeyRef:
                name: azure-operator-test-1233
                key: password
```

## 感想

マネージドサービスの恩恵を受けつつInfrastructure as Codeを大きく進めるかなりよい機能だと思う。
AWS EKSよりAzureのkubernetes(AKS)を採用する理由の1つになると思う。
(Azure Service Operator自体はEKS上でも動作するが、やはりマネージドサービスと
kubernetesクラスタを同じクラウドに乗せるほうが楽)   

追記: AWSも[こういうの]( https://github.com/aws/aws-controllers-k8s)出してた。。。(まだDeveloper Previewとのことだけど)


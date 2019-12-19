Spring Frameworkをjdbでデバックする
-------------------------------------------

Spring Frameworkで作られたwebアプリをデバックする必要があったが、
宗教上の理由でEclipseが使用できなかったのでメモ


以下でjarを作る。  

```
gradle bootJar
```

作成されたjarを以下のように起動することで、8001ポートでデバックを受け付ける。  

```
java -Xdebug -Xrunjdwp:transport=dt_socket,server=y,address=8001,suspend=y -jar build/libs/app-1.0.0.jar
```

jdbでアタッチ  

```
jdb -attach 127.0.0.1:8001
```


アプリケーションの開始  

```
main[1] next
```

ブレークポイントの設定  

```
> stop at com.example.app.web.controller.HomeController:50
Set breakpoint com.example.app.web.controller.HomeController:50
>
Breakpoint hit: "thread=http-nio-8080-exec-3", com.example.app.web.controller.HomeController.ajax(), line=50 bci=6
```


値の参照  

```
http-nio-8080-exec-3[1] print variableName
```


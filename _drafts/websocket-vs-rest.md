https://github.com/tinode/chat

### Login

```
{"login":{"id":"****","scheme":"basic","secret":"**********"}}
```


sending message
```
{"pub":{"id":"****","topic":"grp******","noecho":true,"content":"sample"}}
```


### create room

```
{"sub":{"id":"****","topic":"new102180","set":{"desc":{"public":{"fn":"サンプル","note":"ディスクリプション","photo":{"data":"␡","ref":"/v0/file/s/yz3lDwrCX6c.png","type":"jpeg"}},"private":{"comment":"コメント"}}},"get":{"data":{"limit":24},"what":"data sub desc"}}}
```

file upload
https://web.tinode.co/v0/file/u/
POST

```
{
    "ctrl": {
        "id": "102179",
        "params": {
            "expires": "2023-04-22T06:09:21.962",
            "url": "/v0/file/s/yz3lDwrCX6c.png"
        },
        "code": 200,
        "text": "ok",
        "ts": "2023-04-22T06:08:21.962Z"
    }
}
```

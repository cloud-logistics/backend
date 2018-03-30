## 告警消息通知API

### 1. 获取告警通知列表

#### 方法：
 
`GET`

#### URL：

`container/api/v1/cloudbox/tms/notify/list/{user_id}`

#### BODY:



#### 响应：

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "count": 3,
        "limit": 10,
        "results": [
            {
                "notify_id": 13,
                "time": "2018-03-27T15:06:43.289910+08:00",
                "title": "云箱告警",
                "content": "当前温度：30.0，超过最高温度阈值：15.00;",
                "deviceid": "dev1",
                "qr_id": "123456789",
                "read_flag": "N",
                "user": "2"
            },
            {
                "notify_id": 12,
                "time": "2018-03-27T15:02:10.062420+08:00",
                "title": "云箱告警",
                "content": "当前温度：30.0，超过最高温度阈值：15.00;",
                "deviceid": "dev1",
                "qr_id": "123456789",
                "read_flag": "N",
                "user": "2"
            },
            {
                "notify_id": 11,
                "time": "2018-03-27T14:35:40.348732+08:00",
                "title": "云箱告警",
                "content": "当前温度：30.0，超过最高温度阈值：15.00;",
                "deviceid": "dev1",
                "qr_id": "123456789",
                "read_flag": "N",
                "user": "2"
            }
        ],
        "links": {
            "previous": null,
            "next": "http://106.2.20.185:8000/container/api/v1/cloudbox/tms/notify/list/2?limit=10&offset=10"
        },
        "offset": 0
    }
}

```


### 2. 修改通知消息已读标志：

#### URL：

`container/api/v1/cloudbox/tms/notify/set`

#### 方法： 

`POST`

#### BODY:

```
{
    "notify_id": "1",
	"read_flag" : "Y"
}
```
 
#### 返回：

```
{
    "status": "OK",
    "msg": "update notify success."
}
```

### 3. 删除通知消息：

#### URL：

`container/api/v1/cloudbox/tms/notify/delete/{notify_id}`

#### 方法： 

`DELETE`

#### BODY:

```

```
 
#### 返回：

```
{
    "status": "OK",
    "msg": "delete notify success."
}
```
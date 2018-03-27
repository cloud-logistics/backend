## 消息通知API

### 1. 获取通知列表

#### 方法：
 
`GET`

#### URL：

`container/api/v1/cloudbox/tms/notify/list/{user_id}`

#### BODY:



#### 响应：

```
{
    "status": "OK",
    "msg": "get fishery list success.",
    "data": [
        {
            "latitude": "18.20000",
            "fishery_name": "三亚渔场",
            "longitude": "109.50000",
            "fishery_id": 2
        },
        {
            "latitude": "20.01667",
            "fishery_name": "海口渔场",
            "longitude": "110.35000",
            "fishery_id": 1
        }
    ]
}


```

```
{
    "status": "ERROR",
    "msg": "error msg"
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
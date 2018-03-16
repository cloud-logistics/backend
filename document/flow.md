## 流程API

### 1. 获取渔场列表

#### 方法：
 
`GET`

#### URL：

`container/api/v1/cloudbox/tms/fisherylist`

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

### 2. 获取虾种类列表：

#### URL：

`container/api/v1/cloudbox/tms/fishtypelist`

#### 方法： 

`GET`

#### BODY:

 
#### 返回：

```
{
    "status": "OK",
    "msg": "get fish type list success.",
    "data": [
        {
            "type_name": "皮皮虾",
            "type_id": 1
        },
        {
            "type_name": "基围虾",
            "type_id": 2
        }
    ]
}
```


### 3. 获取单位列表：

#### URL： 

`container/api/v1/cloudbox/tms/unitlist`

#### 方法： 

`GET`

#### BODY:

`无`

#### 返回：
```
{
    "status": "OK",
    "msg": "get unit list success.",
    "data": [
        {
            "unit_name": "千克",
            "unit_id": 1
        }
    ]
}
```


### 4. 捕捞：

#### URL：

`container/api/v1/cloudbox/tms/fishing?user_id=123`

#### 方法： 

`POST`

#### BODY:

```
{
	"qr_id" : "1234566",
    "fish_type_id": 1,
    "fishery_id": 1,
    "weight": 12.34,
    "unit_id": 1
}
```
 
#### 返回：

```
{
    "status": "OK",
    "msg": "fishing report success."
}
```

### 5. 装载：

#### URL：

`container/api/v1/cloudbox/tms/loadup?user_id=123`

#### 方法： 

`POST`

#### BODY:

```
{
	"qr_id" : "1234566",
    "flume_id": 1
}
```
 
#### 返回：

```
{
    "status": "OK",
    "msg": "loadup report success."
}
```


### 6. 卸载：

#### URL：

`container/api/v1/cloudbox/tms/loadoff?user_id=123`

#### 方法： 

`POST`

#### BODY:

```
{
	"qr_id" : "1234566"
}
```
 
#### 返回：

```
{
    "status": "OK",
    "msg": "loadup report success."
}
```

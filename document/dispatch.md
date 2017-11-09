## 云箱调度

### 1. 查询仓库当天调度：

#### URL：

`container/api/v1/cloudbox/dispatch`

#### 方法：

`GET`

#### BODY:

`无`

#### 返回：

```
{
    "message": "query dispatch success",
    "code": "OK",
    "data": {
        "count": 1,
        "limit": 10,
        "results": [
            {
                "did": 13,
                "start": {
                    "id": 10,
                    "location": "廊坊堆场",
                    "longitude": "116.684922",
                    "latitude": "39.537800",
                    "site_code": "LF001"
                },
                "finish": {
                    "id": 30,
                    "location": "test1234",
                    "longitude": "120.00",
                    "latitude": "40.00",
                    "site_code": "TS1111"
                },
                "count": 100,
                "status": "undispatch",
                "create_date": "2017-11-09"
            }
        ],
        "links": {
            "previous": null,
            "next": null
        },
        "offset": 0
    }
}
```

### 2. 查询仓库调度历史：

#### URL：

`container/api/v1/cloudbox/disHistory`

#### 方法：

`GET`

#### BODY:

`无`

#### 返回：

```
{
    "status": "OK",
    "msg": "query dispatches success",
    "dispatches": [
        {
            "did": 7,
            "start": {
                "id": 7,
                "location": "潍坊堆场",
                "longitude": "119.160459",
                "latitude": "36.710008",
                "site_code": "WF001"
            },
            "finish": {
                "id": 8,
                "location": "滨州堆场",
                "longitude": "117.970763",
                "latitude": "37.381072",
                "site_code": "BZ001"
            },
            "count": 2,
            "status": "undispatch",
            "create_date": "2017-11-03"
        },
        {
            "did": 8,
            "start": {
                "id": 9,
                "location": "沧州堆场",
                "longitude": "116.838607",
                "latitude": "38.306742",
                "site_code": "CZ001"
            },
            "finish": {
                "id": 10,
                "location": "廊坊堆场",
                "longitude": "116.684922",
                "latitude": "39.537800",
                "site_code": "LF001"
            },
            "count": 5,
            "status": "undispatch",
            "create_date": "2017-11-03"
        }
    ]
}
```

### 1. 手持机定时查询运营平台获取调度信息接口：

#### URL：

` http://106.2.20.186:8000/container/api/v1/cloudbox/querydispatch/{site_id}`

#### 方法：

`GET`

#### BODY:

`无`

#### 返回：

```

{
    "result": "True",
    "code": "000000",
    "msg": "Success",
    "dispatch_id": 1234,
    "count": 10
}

```

### 2. 调度出仓接口

#### 方法：

`POST`

#### URL：

`http://106.2.20.186:8000/container/api/v1/cloudbox/dispatchout`

#### BODY:

```
{
    "dispatch_id": 12,
    "boxes": [
        {"box_id": "HNAF0000284"}, 
        {"box_id": "HNAR0000247"}
    ]
}
```

#### 响应：

```
{
    "result": "True",
    "code": "000000",
    "msg": "Success",
    "status": "dispatch"
}
```


### 3. 调度入仓接口

#### 方法：

`POST`

#### URL：

`http://106.2.20.186:8000/container/api/v1/cloudbox/dispatchin`

#### BODY:

```
{
    "dispatch_id": 12,
    "boxes": [
        {"box_id": "HNAF0000284"}, 
        {"box_id": "HNAR0000247"}
    ]
}
```

#### 响应：

```
{
    "result": "True",
    "code": "000000",
    "msg": "Success"
}
```


### 4. 云箱进出仓接口

#### 方法：

`POST`

#### URL：

`container/api/v1/cloudbox/boxinout`

#### BODY:

```
{
"site_id": "7",
"boxes": [
	{"box_id": "HNAF0000284",
	 "type": "1"
	},
	{"box_id": "HNAR0000247",
	 "type": "1"
	}
	]
}
```


#### 响应：

```
{
    "status": "OK",
    "msg": "post box inout success"
}
```





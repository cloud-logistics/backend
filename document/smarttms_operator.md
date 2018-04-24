## 运营方查询API

### 1. 首页

#### 方法：
 
`GET`

#### URL：

`container/api/v1/cloudbox/smarttms/operator/home_page`

#### BODY:
`无`
#### 响应：

```
{
    "message": "Succ",
    "code": "0000",
    "data": [
        {
            "status": "正常",
            "box_type_name": "冷藏箱",
            "temperature_threshold_max": 30,
            "deviceid": "8647970359646630",
            "type_id": 1,
            "latitude": "0",
            "temperature_threshold_min": 3,
            "longitude": "0",
            "temperature": 26.7
        },
        {
            "status": "正常",
            "box_type_name": "冷冻箱",
            "temperature_threshold_max": 0,
            "deviceid": "test",
            "type_id": 2,
            "latitude": "0",
            "temperature_threshold_min": -10,
            "longitude": "0",
            "temperature": 0
        }
    ]
}
```


### 2. 云箱状态

#### URL：

`container/api/v1/cloudbox/smarttms/operator/box_status`

#### 方法： 

`GET`

#### BODY:
 `无`
#### 返回：

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "used_box": [],
        "unused_box": [
            {
                "box_type_name": "冷藏箱",
                "num": 1,
                "id": 1
            },
            {
                "box_type_name": "冷冻箱",
                "num": 1,
                "id": 2
            }
        ]
    }
}

```


### 3. 云箱类型名称查询

#### URL：

`container/api/v1/cloudbox/smarttms/operator/box_detail?deviceid=test`

#### 方法： 

`GET`

#### 参数
`deviceid: 云箱id `

#### BODY:
 `无`
#### 返回：

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "box_type_name": "冷冻箱",
        "type_id": 2
    }
}

```

```
{
    "message": "Fail",
    "code": "9999",
    "data": "deviceid not found"
}

```

### 4. 扫码用箱
#### URL：

`container/api/v1/cloudbox/smarttms/operator/box_rent`

#### 方法： 

`POST`

#### BODY:
```
{
	"appointment_id": "appointment_id1",
	"data": [{
		"box_type_id": 1,
		"deviceid_list": ["8647970359646630"]
	}, {
		"box_type_id": 2,
		"deviceid_list": ["test"]
	}]
}
```
#### 返回：
```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "box_order_id": "0208af59-4797-11e8-accf-6a000286eb10"
    }
}
```

```
{
    "message": "Fail",
    "code": "9999",
    "data": "deviceid:8647970359646630 is being used"
}
```

```
{
    "message": "Fail",
    "code": "9999",
    "data": "box number error"
}

```



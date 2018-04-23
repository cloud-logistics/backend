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
    "data": [
        {
            "box_type_name": "冷藏箱",
            "temperature_threshold_max": 30,
            "deviceid": "8647970359646630",
            "type_id": 1,
            "latitude": "0",
            "status_code": 0,
            "temperature_threshold_min": 3,
            "longitude": "0",
            "temperature": 26.1
        },
        {
            "box_type_name": "冷冻箱",
            "temperature_threshold_max": 0,
            "deviceid": "test",
            "type_id": 2,
            "latitude": "0",
            "status_code": 0,
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
}```


## 订单查询API

### 1. 获取在运/已完成订单虾盒列表

#### 方法：
 
`GET`

#### URL：

`container/api/v1/cloudbox/tms/get_order?user_id=1&order_status=1`
##### parameter:
```
user_id: 登录用户id
order_status:  0 在运  1 已完成
```

#### BODY:
`无`
#### 响应：

```
{
    "message": "Succ",
    "code": "0000",
    "data": [
        {
            "fishery_name": "海口捕捞场",
            "unit": "KG",
            "type_name": "南美白对虾",
            "weight": "20.02",
            "qr_id": "QR01"
        }
    ]
}


```

```
{
    "message": "Fail",
    "code": "9999",
    "data": "server internal error, pls contact admin"
}
```

### 2. 获取订单详情：

#### URL：

`container/api/v1/cloudbox/tms/order_detail?qr_id=QR01`

#### 方法： 

`GET`
##### parameter:
```
qr_id: 订单id
```

#### BODY:
 `无`
#### 返回：

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "unit_name": "KG",
        "fishery_name": "海口捕捞场",
        "op_list": [
            {
                "timestamp": 1521104363,
                "op_type_flag": 1,
                "user_name": "fishman01",
                "op_type": "捕捞"
            },
            {
                "timestamp": 1521104364,
                "op_type_flag": 2,
                "user_name": "driver01",
                "op_type": "装车"
            },
            {
                "timestamp": 1521430200,
                "op_type_flag": 3,
                "user_name": "merchant01",
                "op_type": "商家收货"
            }
        ],
        "weight": "20.02",
        "fish_type_name": "南美白对虾"
    }
}
```

```
{
    "message": "Fail",
    "code": "9999",
    "data": "server internal error, pls contact admin"
}
```

### 3. 获取指标历史曲线：

#### URL： 

`container/api/v1/cloudbox/tms/indicator_history?qr_id=QR01&indicator_type=dissolved_oxygen`

#### 方法： 

`GET`
##### parameter:
```
qr_id: 订单id
indicator_type：salinity、ph、dissolved_oxygen、temperature
```

#### BODY:

`无`

#### 返回：
```
返回固定20个时间点的数据，20个点是从订单开始时间到结束时间均匀分布
{
    "message": "Succ",
    "code": "0000",
    "data": [
        {
            "value": "0.20",
            "time": "2018-03-15 16:59~2018-03-15 21:30"
        },
        ...
        {
            "value": "NA",
            "time": "2018-03-19 06:58~2018-03-19 11:30"
        }
    ]
}
```

```
{
    "message": "Fail",
    "code": "9999",
    "data": "server internal error, pls contact admin"
}
```

### 4. 获取订单数量统计信息：

#### URL：

`container/api/v1/cloudbox/tms/order_statistic?user_id=4`

#### 方法：

`GET`
##### parameter:
```
user_id: 用户id
```

#### BODY:

`无`

#### 返回：
```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "done_num": 1,
        "ongoing_num": 1,
        "notice_num": 0
    }
}
```

```
{
    "message": "Fail",
    "code": "9999",
    "data": "server internal error, pls contact admin"
}
```


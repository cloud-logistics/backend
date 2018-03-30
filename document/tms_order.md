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
            "delivery_timestamp": 1521535017,
            "fishing_timestamp": 1521533853,
            "load_timestamp": 1521534906,
            "weight": "12.34",
            "qr_id": "123",
            "fishery_name": "海口渔场",
            "type_name": "南美白对虾",
            "unit": "千克"
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

### 5. 获取在运虾盒指标当前值：

#### URL：

`container/api/v1/cloudbox/tms/current_status?qr_id=123`

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
        "ph": "3.14",
        "dissolved_oxygen": "9.93",
        "temperature": "12.24",
        "salinity": "7.45"
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


### 6. 获取在运虾盒运行轨迹：

#### URL：

`container/api/v1/cloudbox/tms/history_path?qr_id=123`

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
    "data": [
        {
            "latitude": "20.01667",
            "timestamp": 0,
            "longitude": "110.35000"
        },
        ...
        {
            "timestamp": 1521699600,
            "longitude": "128.452865",
            "latitude": "27.465556"
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




### 7. 获取阈值列表：

#### URL：

`container/api/v1/cloudbox/tms/threshold_list`

#### 方法：

`GET`

#### BODY:

`无`

#### 返回：
```
{
    "message": "Succ",
    "code": "0000",
    "data": [
        {
            "type_id": 3,
            "type_name": "test",
            "salinity_min": "0.10",
            "salinity_max": "2.00",
            "ph_min": "3.00",
            "ph_max": "7.00",
            "dissolved_oxygen_min": "2.00",
            "dissolved_oxygen_max": "4.00",
            "temperature_min": "8.00",
            "temperature_max": "10.00"
        },
        ...
        {
            "type_id": 2,
            "type_name": "基围虾",
            "salinity_min": "2.00",
            "salinity_max": "10.00",
            "ph_min": "2.00",
            "ph_max": "4.00",
            "dissolved_oxygen_min": "0.10",
            "dissolved_oxygen_max": "10.00",
            "temperature_min": "2.00",
            "temperature_max": "30.00"
        }
    ]
}
```



### 8. 添加阈值：

#### URL：

`container/api/v1/cloudbox/tms/threshold`

#### 方法：

`POST`

#### BODY:

```
{
	"type_name": "test",
	"salinity_min": 0.1,
	"salinity_max": 2,
	"ph_min": 3,
	"ph_max": 7,
	"dissolved_oxygen_min": 2,
	"dissolved_oxygen_max": 4,
	"temperature_min": 8,
	"temperature_max": 10
}
```

#### 返回：
```
{
    "message": "Succ",
    "code": "0000",
    "data": "save fish type threshold successfully"
}
```

```
{
    "message": "Fail",
    "code": "9999",
    "data": "type_name [test] already exists"
}
```



### 9. 修改阈值：

#### URL：

`container/api/v1/cloudbox/tms/threshold/<type_id>`

#### 方法：

`POST`

#### BODY:

```
{	
	"salinity_min": 0.1,
	"salinity_max": 2,
	"ph_min": 3,
	"ph_max": 7,
	"dissolved_oxygen_min": 2,
	"dissolved_oxygen_max": 4,
	"temperature_min": 8,
	"temperature_max": 10
}
```

#### 返回：
```
{
    "message": "Succ",
    "code": "0000",
    "data": "modify fish type threshold successfully"
}
```

```
{
    "message": "Fail",
    "code": "9999",
    "data": "server internal error, pls contact admin"
}
```



### 10. 删除阈值：

#### URL：

`container/api/v1/cloudbox/tms/threshold/<type_id>/`

#### 方法：

`DELETE`

#### BODY:

```
无
```

#### 返回：
```
{
    "message": "Succ",
    "code": "0000",
    "data": "delete fish type threshold successfully"
}
```

```
{
    "message": "Fail",
    "code": "9999",
    "data": "Fish Type is being used, can't be deleted"
}
```

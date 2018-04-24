## 发货方

### 1. 获取云箱列表

#### 方法：
 
`GET`

#### URL：

`container/api/v1/cloudbox/smarttms/shipper/boxlist?user_id=`

#### BODY:

`无`

#### 响应：

```
{
    "status": "OK",
    "msg": "Get box list success.",
    "using": [
        {
            "deviceid": "",
            "latitude": "18.20000",
            "longitude": "109.50000",
            "type_name": "",
            "status": ""
        },
        {
            "deviceid": "",
            "latitude": "20.01667",
            "longitude": "110.35000",
            "type_name": "",
            "status": ""
        }
    ],
    "transporting": [
        {
            "deviceid": "",
            "latitude": "18.20000",
            "longitude": "109.50000",
            "type_name": "",
            "status": ""
        },
        {
            "deviceid": "",
            "latitude": "20.01667",
            "longitude": "110.35000",
            "type_name": "",
            "status": ""
        }
    ],
    "unused": [
        {
            "deviceid": "",
            "latitude": "18.20000",
            "longitude": "109.50000",
            "type_name": "",
            "status": ""
        },
        {
            "deviceid": "",
            "latitude": "20.01667",
            "longitude": "110.35000",
            "type_name": "",
            "status": ""
        }
    ]
}

```


### 2. 根据云箱ID获取云箱详情

#### 方法：
 
`GET`

#### URL：

`container/api/v1/cloudbox/smarttms/shipper/boxdetail?user_id=&deviceid=`

#### BODY:

`无`

#### 响应：

```
{
    "status": "OK",
    "msg": "Get box detail success.",
    "data": {
                "deviceid": "",
                "latitude": "18.20000",
                "longitude": "109.50000",
                "use_time": 123,
                "status": "",
                "shop_tel" : "18092049581"
            }
}

```


### 3. 获取门店列表

#### 方法：
 
`GET`

#### URL：

`container/api/v1/cloudbox/smarttms/shipper/shoplist?user_id=`

#### BODY:

`无`

#### 响应：

```
{
    "status": "OK",
    "msg": "Get shop list success.",
    "data": [
        {
            "shop_id": "",
            "shop_name": "",
            "shop_location": ""
        },
        {
            "shop_id": "",
            "shop_name": "",
            "shop_location": ""
        }
    ]
}

```


### 4. 获取货物列表

#### 方法：
 
`GET`

#### URL：

`container/api/v1/cloudbox/smarttms/shipper/goodslist?user_id=`

#### BODY:

`无`

#### 响应：

```
{
    "status": "OK",
    "msg": "Get goods list success.",
    "data": [
        {
            "goods_id": 1,
            "goods_name": "",
            "ava_number": 123,
            "goods_unit": ""
        },
        {
            "goods_id": 2,
            "goods_name": "",
            "ava_number": 123,
            "goods_unit": ""
        }
    ]
}

```

### 5. 结束装箱,生成运单

#### 方法：
 
`POST`

#### URL：

`container/api/v1/cloudbox/smarttms/shipper/goodsorder`

#### BODY:

```
{
    "user_id": "shipper",
    "shop_id": 12,
    "site_id": 11,
    "boxes": [
        {
            "deviceid": "",
            "goods": [
                {
                    "goods_id": "",
                    "goods_num": 1
                },
                {
                    "goods_id": "",
                    "goods_num": 2
                }
            ]
        },
        {
            "deviceid": "",
            "goods": [
                {
                    "goods_id": "",
                    "goods_num": 3
                },
                {
                    "goods_id": "",
                    "goods_num": 4
                }
            ]
        }
    ]
}

```

#### 响应：

```
{
    "status": "OK",
    "msg": "Add goods order success."
}

```

### 6. 获取已经生产的运单列表

#### 方法：
 
`GET`

#### URL：

`container/api/v1/cloudbox/smarttms/shipper/orderlist?user_id=`

#### BODY:

`无`

#### 响应：

```
{
    "status": "OK",
    "msg": "Get order list success.",
    "data": [
        {
            "order_id": "",
            "order_time": "",
            "shop_id": 123,
            "shop_name": "",
            "status": "",
            "goods": [
                {
                    "goods_id": 1,
                    "goods_name": "",
                    "goods_unit": "",
                    "number": 123
                },
                {
                    "goods_id": 1,
                    "goods_name": "",
                    "goods_unit": "",
                    "number": 123
                }
            ]
        },
        {
            "order_id": "",
            "order_time": "",
            "shop_id": 123,
            "shop_name": "",
            "status": "",
            "goods": [
                {
                    "goods_id": 2,
                    "goods_name": "",
                    "goods_unit": "",
                    "number": 123
                }
            ]
        }
    ]
}

```


### 7. 修改运单

#### 方法：
 
`PUT`

#### URL：

`container/api/v1/cloudbox/smarttms/shipper/goodsorder/{order_id}`

#### BODY:

```
{
    "user_id": "shipper",
    "site_id": 11,
    "shop_id": 12,
    "boxes": [
        {
            "deviceid": "",
            "goods": [
                {
                    "goods_id": "",
                    "goods_num": 1
                },
                {
                    "goods_id": "",
                    "goods_num": 2
                }
            ]
        },
        {
            "deviceid": "",
            "goods": [
                {
                    "goods_id": "",
                    "goods_num": 3
                },
                {
                    "goods_id": "",
                    "goods_num": 4
                }
            ]
        }
    ]
}

```

#### 响应：

```
{
    "status": "OK",
    "msg": "Update goods order success."
}

```


### 8. 删除运单

#### 方法：
 
`DELETE`

#### URL：

`container/api/v1/cloudbox/smarttms/shipper/goodsorder/{order_id}`

#### BODY:

```
无
```

#### 响应：

```
{
    "status": "OK",
    "msg": "Delete goods order success."
}

```


### 9. 获取所有发货单列表

#### 方法：
 
`GET`

#### URL：

`container/api/v1/cloudbox/smarttms/shipper/allorder?user_id=`

#### BODY:

`无`

#### 响应：

```
{
    "status": "OK",
    "msg": "Get all order list success.",
    "data": [
        {
            "order_id": "",
            "order_time": "",
            "shop_id": 123,
            "shop_name": "",
            "status": "",
            "driver_name": "",
            "driver_tel": "18099992222",
            "goods": [
                {
                    "goods_id": 1,
                    "goods_name": "",
                    "number": 123
                },
                {
                    "goods_id": 1,
                    "goods_name": "",
                    "number": 123
                }
            ]
        },
        {
            "order_id": "",
            "shop_id": 123,
            "shop_name": "",
            "status": "",
            "driver_name": "",
            "driver_tel": "18099992222",
            "goods": [
                {
                    "goods_id": 2,
                    "goods_name": "",
                    "number": 123
                }
            ]
        }
    ]
}

```


### 10. 按天查询发货单列表

#### 方法：
 
`GET`

#### URL：

`container/api/v1/cloudbox/smarttms/shipper/orders_by_day?user_id=&day=`

#### BODY:

`无`

#### 响应：

```
{
    "status": "OK",
    "msg": "Get order list by day success.",
    "data": [
        {
            "order_id": "",
            "shop_id": 123,
            "shop_name": "",
            "status": "",
            "driver_name": "",
            "driver_tel": "18099992222",
            "goods": [
                {
                    "goods_id": 1,
                    "goods_name": "",
                    "number": 123
                },
                {
                    "goods_id": 1,
                    "goods_name": "",
                    "number": 123
                }
            ]
        },
        {
            "order_id": "",
            "shop_id": 123,
            "shop_name": "",
            "status": "",
            "driver_name": "",
            "driver_tel": "18099992222",
            "goods": [
                {
                    "goods_id": 2,
                    "goods_name": "",
                    "number": 123
                }
            ]
        }
    ]
}

```


### 11. 根据货单ID查询货单详情

#### 方法：
 
`GET`

#### URL：

`container/api/v1/cloudbox/smarttms/shipper/order_detail?user_id=&order_id=`

#### BODY:

`无`

#### 响应：

```
{
    "status": "OK",
    "msg": "Get order detail success.",
    "data": 
        {
            "order_id": "",
            "shop_id": 123,
            "shop_name": "",
            "shop_tel": "18099991111",
            "arrive_time": "",
            "status": "",
            "driver_name": "",
            "driver_tel": "18099992222",
            "boxes": [
                {
                    "deviceid": "",
                    "box_type": "",
                    "temperature": 12.0,
                    "humidity": 10.0,
                    "goods": [
                        {
                            "goods_id": "",
                            "goods_name": "",
                            "goods_num": 1
                        },
                        {
                            "goods_id": "",
                            "goods_name": "",
                            "goods_num": 2
                        }
                    ]
                },
                {
                    "deviceid": "",
                    "box_type": "",
                    "temperature": 12.0,
                    "humidity": 10.0,
                    "goods": [
                        {
                            "goods_id": "",
                            "goods_name": "",
                            "goods_num": 3
                        },
                        {
                            "goods_id": "",
                            "goods_name": "",
                            "goods_num": 4
                        }
                    ]
                }
            ]
        
        }
}

```






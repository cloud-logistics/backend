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
        "status": "正常",
        "shop_tel": "1234",
        "longitude": "113.934656",
        "use_time": 35940,
        "deviceid": "8647970359646630",
        "latitude": "22.518395"
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
    "message": "Get shop list success.",
    "code": "OK",
    "data": {
        "count": 3,
        "limit": 10,
        "results": [
            {
                "shop_id": 1,
                "shop_location": "印象城",
                "shop_name": "河马鲜生"
            },
            {
                "shop_id": 2,
                "shop_location": "万达",
                "shop_name": "海底捞"
            },
            {
                "shop_id": 3,
                "shop_location": "高新",
                "shop_name": "大排档"
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
    "message": "Get goods list success.",
    "code": "OK",
    "data": {
        "count": 3,
        "limit": 2,
        "results": [
            {
                "ava_number": 100,
                "goods_name": "麻辣小龙虾",
                "goods_id": "1",
                "goods_unit": "件"
            },
            {
                "ava_number": 500,
                "goods_name": "秋刀鱼",
                "goods_id": "2",
                "goods_unit": "件"
            }
        ],
        "links": {
            "previous": null,
            "next": "http://106.2.20.185:8000/container/api/v1/cloudbox/smarttms/shipper/goodslist?limit=2&offset=2"
        },
        "offset": 0
    }
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
    "user_id": "20927c0c-4761-11e8-aafd-525400bbac8e",
    "shop_id": 1,
    "site_id": 1,
    "boxes": [
        {
            "deviceid": "8647970359646630",
            "goods": [
                {
                    "goods_id": "1",
                    "goods_num": 10
                },
                {
                    "goods_id": "2",
                    "goods_num": 20
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
    "message": "Get order list success.",
    "code": "OK",
    "data": {
        "count": 1,
        "limit": 10,
        "results": [
            {
                "status": "正常",
                "shop_tel": "1234",
                "goods": [
                    {
                        "number": 10,
                        "goods_name": "麻辣小龙虾",
                        "goods_id": "1",
                        "goods_unit": "件"
                    },
                    {
                        "number": 25,
                        "goods_name": "秋刀鱼",
                        "goods_id": "2",
                        "goods_unit": "件"
                    }
                ],
                "order_time": "2018-04-25T02:10:25.677980Z",
                "order_id": "d1496ed0-482d-11e8-aafd-525400bbac8e",
                "shop_name": "河马鲜生",
                "shop_id": 1
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

`container/api/v1/cloudbox/smarttms/shipper/goodsorder/{order_id}/`

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

`container/api/v1/cloudbox/smarttms/shipper/allgoodsorder?user_id=`

#### BODY:

`无`

#### 响应：

```
{
    "message": "Get transporting order list success.",
    "code": "OK",
    "data": {
        "count": 1,
        "limit": 10,
        "results": [
            {
                "status": "正常",
                "driver_name": "driver1",
                "shop_tel": "1234",
                "shop_id": 1,
                "driver_tel": "123456",
                "order_time": "2018-04-25T02:10:25.677980Z",
                "goods": [
                    {
                        "number": 10,
                        "goods_name": "麻辣小龙虾",
                        "goods_id": "1",
                        "goods_unit": "件"
                    },
                    {
                        "number": 25,
                        "goods_name": "秋刀鱼",
                        "goods_id": "2",
                        "goods_unit": "件"
                    }
                ],
                "order_id": "d1496ed0-482d-11e8-aafd-525400bbac8e",
                "shop_name": "河马鲜生"
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


### 10. 按天查询发货单列表

#### 方法：
 
`GET`

#### URL：

`container/api/v1/cloudbox/smarttms/shipper/orders_by_day?user_id=&begin_time=&end_time=`

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

`container/api/v1/cloudbox/smarttms/shipper/goodsorder/{order_id}`

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







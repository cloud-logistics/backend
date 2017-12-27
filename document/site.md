## 仓库API

### 1. 增加仓库

#### 方法：

`POST`

#### URL：

`container/api/v1/cloudbox/monservice/sites`

#### BODY:

```
 {
	"location": "西安堆场",
	"longitude": "120.0000",
	"latitude": "30.0000",
	"site_code": "",
	"volume": 500,
	"city_id": 1,
	"province_id": 1,
	"nation_id": 1
}
```

#### 响应：

```
{
    "status": "OK",
    "msg": "add site success"
}
```

```
{
    "status": "ERROR",
    "msg": "error msg"
}
```

### 2. 修改仓库：

#### URL：

`container/api/v1/cloudbox/monservice/sites/{site_id}/`

#### 方法：

`PUT`

#### BODY:

```
{
	"location": "测试666",
	"longitude": "120.00",
	"latitude": "30.00",
	"site_code": "",
	"volume": 500,
	"city_id": 1,
	"province_id": 1,
	"nation_id": 1
}
 ```

#### 返回：

```
{
    "status": "OK",
    "msg": "modify site success"
}
```


### 3. 删除仓库：

#### URL：

`container/api/v1/cloudbox/monservice/sites/{site_id}`

#### 方法：

`DELETE`

#### BODY:

`无`

#### 返回：
```
{
    "status": "OK",
    "msg": "delete site success"
}
```

### 4. 查询仓库：

#### URL：

`container/api/v1/cloudbox/monservice/allsites?page=2`

#### 方法：

`GET`

#### BODY:



#### 返回：
```
{
    "message": "query sites success",
    "code": "OK",
    "data": {
        "count": 20,
        "num_pages": 2,
        "results": [
            {
                "id": 1,
                "city": {
                    "id": 1,
                    "city_name": "北京",
                    "state_name": "北京",
                    "nation_name": "中国",
                    "longitude": "116.4073963",
                    "latitude": "39.9041999",
                    "area_name": "亚洲",
                    "culture": "",
                    "taboo": "",
                    "picture_url": "",
                    "sorted_key": "b",
                    "flag": 0,
                    "nation": 1,
                    "province": 1
                },
                "province": {
                    "province_id": 1,
                    "province_name": "北京市",
                    "zip_code": "110000",
                    "nation": 1
                },
                "nation": {
                    "nation_id": 1,
                    "nation_name": "中国",
                    "pic_url": "http://ouq3fowh7.bkt.clouddn.com/%E5%9B%BD%E5%86%85.png",
                    "sorted_key": "z"
                },
                "location": "北京朝阳区堆场",
                "latitude": "39.92111",
                "longitude": "116.46111",
                "site_code": "BJ001",
                "volume": 0
            },
            {
                "id": 2,
                "city": {
                    "id": 1,
                    "city_name": "北京",
                    "state_name": "北京",
                    "nation_name": "中国",
                    "longitude": "116.4073963",
                    "latitude": "39.9041999",
                    "area_name": "亚洲",
                    "culture": "",
                    "taboo": "",
                    "picture_url": "",
                    "sorted_key": "b",
                    "flag": 0,
                    "nation": 1,
                    "province": 1
                },
                "province": {
                    "province_id": 1,
                    "province_name": "北京市",
                    "zip_code": "110000",
                    "nation": 1
                },
                "nation": {
                    "nation_id": 1,
                    "nation_name": "中国",
                    "pic_url": "http://ouq3fowh7.bkt.clouddn.com/%E5%9B%BD%E5%86%85.png",
                    "sorted_key": "z"
                },
                "location": "北京海淀区堆场",
                "latitude": "39.92222",
                "longitude": "116.46222",
                "site_code": "BJ002",
                "volume": 0
            }
        ],
        "links": {
            "previous": null,
            "next": "http://127.0.0.1:8000/container/api/v1/cloudbox/allsites?page=2"
        }
    }
}
```


### 5. 根据仓库查询箱子：

#### URL：

`container/api/v1/cloudbox/monservice/boxbysite/1`

#### 方法：

`GET`

#### BODY:



#### 返回：
```
{
    "message": "query sites box success",
    "code": "OK",
    "data": {
        "count": 2,
        "limit": 10,
        "results": [
            {
                "deviceid": "HNAF0000284",
                "type": {
                    "id": 2,
                    "box_type_name": "冷冻箱",
                    "box_type_detail": "",
                    "interval_time": 30,
                    "temperature_threshold_min": -30,
                    "temperature_threshold_max": 40,
                    "humidity_threshold_min": 3,
                    "humidity_threshold_max": 500,
                    "collision_threshold_min": 0,
                    "collision_threshold_max": 100,
                    "battery_threshold_min": 0,
                    "battery_threshold_max": 1,
                    "operation_threshold_min": 0,
                    "operation_threshold_max": 500,
                    "price": 20,
                    "length": 11,
                    "width": 1.2,
                    "height": 0.8
                },
                "manufacturer": {
                    "id": 1,
                    "name": "深圳市万引力工程技术有限公司"
                },
                "produce_area": {
                    "id": 1,
                    "address": "广东省深圳市龙岗区"
                },
                "hardware": {
                    "id": 1,
                    "hardware_detail": "万引力智能硬件"
                },
                "battery": {
                    "id": 1,
                    "battery_detail": "万引力电源"
                },
                "siteinfo": {
                    "id": 1,
                    "city": {
                        "id": 1,
                        "city_name": "北京",
                        "state_name": "北京",
                        "nation_name": "中国",
                        "longitude": "116.4073963",
                        "latitude": "39.9041999",
                        "area_name": "亚洲",
                        "culture": "",
                        "taboo": "",
                        "picture_url": "",
                        "sorted_key": "b",
                        "flag": 0,
                        "nation": 1,
                        "province": 1
                    },
                    "location": "北京朝阳区堆场",
                    "latitude": "39.92111",
                    "longitude": "116.46111",
                    "site_code": "BJ001",
                    "volume": 0,
                    "province": 1,
                    "nation": 1
                },
                "date_of_production": "1509431998000",
                "carrier": 1,
                "tid": "124",
                "ava_flag": "Y"
            },
            {
                "deviceid": "HNAR0000247",
                "type": {
                    "id": 1,
                    "box_type_name": "冷藏箱",
                    "box_type_detail": "",
                    "interval_time": 30,
                    "temperature_threshold_min": -30,
                    "temperature_threshold_max": 0,
                    "humidity_threshold_min": 3,
                    "humidity_threshold_max": 500,
                    "collision_threshold_min": 0,
                    "collision_threshold_max": 100,
                    "battery_threshold_min": 0,
                    "battery_threshold_max": 1,
                    "operation_threshold_min": 0,
                    "operation_threshold_max": 500,
                    "price": 10,
                    "length": 11,
                    "width": 1.2,
                    "height": 0.8
                },
                "manufacturer": {
                    "id": 1,
                    "name": "深圳市万引力工程技术有限公司"
                },
                "produce_area": {
                    "id": 1,
                    "address": "广东省深圳市龙岗区"
                },
                "hardware": {
                    "id": 1,
                    "hardware_detail": "万引力智能硬件"
                },
                "battery": {
                    "id": 1,
                    "battery_detail": "万引力电源"
                },
                "siteinfo": {
                    "id": 1,
                    "city": {
                        "id": 1,
                        "city_name": "北京",
                        "state_name": "北京",
                        "nation_name": "中国",
                        "longitude": "116.4073963",
                        "latitude": "39.9041999",
                        "area_name": "亚洲",
                        "culture": "",
                        "taboo": "",
                        "picture_url": "",
                        "sorted_key": "b",
                        "flag": 0,
                        "nation": 1,
                        "province": 1
                    },
                    "location": "北京朝阳区堆场",
                    "latitude": "39.92111",
                    "longitude": "116.46111",
                    "site_code": "BJ001",
                    "volume": 0,
                    "province": 1,
                    "nation": 1
                },
                "date_of_production": "1509431998000",
                "carrier": 1,
                "tid": "123",
                "ava_flag": "Y"
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


### 6. 查询仓库箱子流水：

#### URL：

`container/api/v1/cloudbox/monservice/siteStream/1?begin_time=1511944408&end_time=1511947277&op_type=0`

#### 方法：

`GET`

#### BODY:

`无`

#### 返回：

```
{
    "siteHistory": [
        {
            "timestamp": "2017-11-03 12:37:27",
            "box_id": "HNAF0000284",
            "type": "入库"
        },
        {
            "timestamp": "2017-11-03 12:38:51",
            "box_id": "HNAR0000247",
            "type": "出库"
        }
    ],
    "site_id": "1"
}
```



### 7. 查询热力图数据：

#### URL：

`container/api/v1/cloudbox/monservice/distribution`

#### 方法：

`GET`

#### BODY:

`无`

#### 返回：

```
{
    "status": "OK",
    "msg": "query distribution success",
    "sites": [
        {
            "site_code": "BJ001",
            "longitude": "116.46111",
            "location": "北京朝阳区堆场",
            "latitude": "39.92111",
            "box_num": 3000,
            "id": 1
        },
        {
            "site_code": "GZ001",
            "longitude": "113.261870",
            "location": "广州堆场",
            "latitude": "23.131716",
            "box_num": 3000,
            "id": 5
        },
        {
            "site_code": "QD001",
            "longitude": "120.33",
            "location": "青岛堆场",
            "latitude": "36.07",
            "box_num": 3000,
            "id": 6
        },
        {
            "site_code": "WF001",
            "longitude": "119.160459",
            "location": "潍坊堆场",
            "latitude": "36.710008",
            "box_num": 3000,
            "id": 7
        },
        {
            "site_code": "BZ001",
            "longitude": "117.970763",
            "location": "滨州堆场",
            "latitude": "37.381072",
            "box_num": 3000,
            "id": 8
        },
        {
            "site_code": "CZ001",
            "longitude": "116.838607",
            "location": "沧州堆场",
            "latitude": "38.306742",
            "box_num": 3000,
            "id": 9
        },
        {
            "site_code": "LF001",
            "longitude": "116.684922",
            "location": "廊坊堆场",
            "latitude": "39.537800",
            "box_num": 3000,
            "id": 10
        },
        {
            "site_code": "HK001",
            "longitude": "110.290146",
            "location": "海口堆场",
            "latitude": "20.024706",
            "box_num": 3000,
            "id": 11
        },
        {
            "site_code": "WH001",
            "longitude": "114.300457",
            "location": "武汉堆场",
            "latitude": "30.590830",
            "box_num": 3000,
            "id": 12
        },
        {
            "site_code": "JN001",
            "longitude": "117.049018",
            "location": "济南堆场",
            "latitude": "36.662650",
            "box_num": 3000,
            "id": 13
        },
        {
            "site_code": "XA001",
            "longitude": "108.838780",
            "location": "西安堆场",
            "latitude": "34.211539",
            "box_num": 3000,
            "id": 14
        }
    ]
}
```


### 8. 条件查询仓库信息：

#### URL：

`container/api/v1/cloudbox/monservice/querysites?limit=10&offset=0`

#### 方法：

`POST`

#### BODY:

```
{
        "province_id": 1,
        "city_id": 1,
        "min_volume": 0,
        "max_volume": 3000,
        "key_word": "测试"
}

```


##### 字段缺省值：

```
{
        "province_id": 0,
        "city_id": 0,
        "min_volume": -1,
        "max_volume": -1,
        "key_word": ""
}

```


#### 返回：

```
{
    "message": "查询全部仓库成功！",
    "code": "OK",
    "data": {
        "count": 1,
        "limit": 10,
        "results": [
            {
                "id": 145,
                "city": {
                    "id": 1,
                    "city_name": "北京",
                    "state_name": "北京",
                    "nation_name": "中国",
                    "longitude": "116.4073963",
                    "latitude": "39.9041999",
                    "area_name": "亚洲",
                    "culture": "",
                    "taboo": "",
                    "picture_url": "",
                    "sorted_key": "b",
                    "flag": 0,
                    "city_code": null,
                    "nation": 1,
                    "province": 1
                },
                "province": {
                    "province_id": 1,
                    "province_name": "北京市",
                    "zip_code": "110000",
                    "nation": 1
                },
                "nation": {
                    "nation_id": 1,
                    "nation_name": "中国",
                    "pic_url": "http://ouq3fowh7.bkt.clouddn.com/%E5%9B%BD%E5%86%85.png",
                    "sorted_key": "z",
                    "nation_code": null
                },
                "name": "测试222222222222222",
                "location": "425-4 Daejeon-ri, Oeseo-myeon, Sangju, Gyeongsangbuk-do, 韩国",
                "latitude": "39.9041999",
                "longitude": "116.4073963",
                "site_code": "CNBJ000016",
                "volume": 2222,
                "telephone": "12123123"
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




## 仓库接口

### 根据经纬度查询堆场列表

#### METHOD

`GET`

#### URL

`/api/v1/cloudbox/rentservice/site/list/{latitude}/{longitude}`

#### Parameter

pathValue `latitude` 纬度
pathValue `longitude` 经度

#### Return

```
{
    "count": 14,
    "next": "http://localhost:8000/api/v1/cloudbox/rentservice/site/list/34.3829/108.112314?limit=10&offset=10",
    "previous": null,
    "results": [
        {
            "id": 14,
            "city": {
                "id": 308,
                "city_name": "西安",
                "state_name": "陕西",
                "nation_name": "中国",
                "longitude": "108.93977",
                "latitude": "34.341574",
                "area_name": "亚洲",
                "culture": "",
                "taboo": "",
                "picture_url": "",
                "sorted_key": "x",
                "flag": 0,
                "nation": 1,
                "province": 27
            },
            "location": "西安堆场",
            "latitude": "34.211539",
            "longitude": "108.838780",
            "site_code": "XA001",
            "province": 27,
            "nation": 1
        },
        {
            "id": 12,
            "city": {
                "id": 169,
                "city_name": "武汉",
                "state_name": "湖北",
                "nation_name": "中国",
                "longitude": "114.305539",
                "latitude": "30.592849",
                "area_name": "亚洲",
                "culture": "",
                "taboo": "",
                "picture_url": "",
                "sorted_key": "w",
                "flag": 0,
                "nation": 1,
                "province": 17
            },
            "location": "武汉堆场",
            "latitude": "30.590830",
            "longitude": "114.300457",
            "site_code": "WH001",
            "province": 17,
            "nation": 1
        },
        {
            "id": 13,
            "city": {
                "id": 134,
                "city_name": "济南",
                "state_name": "山东",
                "nation_name": "中国",
                "longitude": "117.120095",
                "latitude": "36.6512",
                "area_name": "亚洲",
                "culture": "",
                "taboo": "",
                "picture_url": "",
                "sorted_key": "j",
                "flag": 0,
                "nation": 1,
                "province": 15
            },
            "location": "济南堆场",
            "latitude": "36.662650",
            "longitude": "117.049018",
            "site_code": "JN001",
            "province": 15,
            "nation": 1
        },
        {
            "id": 9,
            "city": {
                "id": 11,
                "city_name": "沧州",
                "state_name": "河北",
                "nation_name": "中国",
                "longitude": "116.838834",
                "latitude": "38.304477",
                "area_name": "亚洲",
                "culture": "",
                "taboo": "",
                "picture_url": "",
                "sorted_key": "c",
                "flag": 0,
                "nation": 1,
                "province": 3
            },
            "location": "沧州堆场",
            "latitude": "38.306742",
            "longitude": "116.838607",
            "site_code": "CZ001",
            "province": 3,
            "nation": 1
        },
        {
            "id": 8,
            "city": {
                "id": 149,
                "city_name": "滨州",
                "state_name": "山东",
                "nation_name": "中国",
                "longitude": "117.970699",
                "latitude": "37.38198",
                "area_name": "亚洲",
                "culture": "",
                "taboo": "",
                "picture_url": "",
                "sorted_key": "b",
                "flag": 0,
                "nation": 1,
                "province": 15
            },
            "location": "滨州堆场",
            "latitude": "37.381072",
            "longitude": "117.970763",
            "site_code": "BZ001",
            "province": 15,
            "nation": 1
        },
        {
            "id": 10,
            "city": {
                "id": 12,
                "city_name": "廊坊",
                "state_name": "河北",
                "nation_name": "中国",
                "longitude": "116.683752",
                "latitude": "39.538047",
                "area_name": "亚洲",
                "culture": "",
                "taboo": "",
                "picture_url": "",
                "sorted_key": "l",
                "flag": 0,
                "nation": 1,
                "province": 3
            },
            "location": "廊坊堆场",
            "latitude": "39.537800",
            "longitude": "116.684922",
            "site_code": "LF001",
            "province": 3,
            "nation": 1
        },
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
            "location": "北京朝阳区堆场",
            "latitude": "39.92111",
            "longitude": "116.46111",
            "site_code": "BJ001",
            "province": 1,
            "nation": 1
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
            "location": "北京海淀区堆场",
            "latitude": "39.92222",
            "longitude": "116.46222",
            "site_code": "BJ002",
            "province": 1,
            "nation": 1
        },
        {
            "id": 3,
            "city": {
                "id": 2,
                "city_name": "天津",
                "state_name": "天津",
                "nation_name": "中国",
                "longitude": "117.3616476",
                "latitude": "39.3433574",
                "area_name": "亚洲",
                "culture": "",
                "taboo": "",
                "picture_url": "",
                "sorted_key": "t",
                "flag": 0,
                "nation": 1,
                "province": 2
            },
            "location": "天津堆场",
            "latitude": "39.129951",
            "longitude": "117.193656",
            "site_code": "TJ001",
            "province": 2,
            "nation": 1
        },
        {
            "id": 7,
            "city": {
                "id": 140,
                "city_name": "潍坊",
                "state_name": "山东",
                "nation_name": "中国",
                "longitude": "119.161748",
                "latitude": "36.706962",
                "area_name": "亚洲",
                "culture": "",
                "taboo": "",
                "picture_url": "",
                "sorted_key": "w",
                "flag": 0,
                "nation": 1,
                "province": 15
            },
            "location": "潍坊堆场",
            "latitude": "36.710008",
            "longitude": "119.160459",
            "site_code": "WF001",
            "province": 15,
            "nation": 1
        }
    ]
}
```

### 根据省、市查询仓库列表

#### METHOD

`GET`

#### URL

`api/v1/cloudbox/rentservice/site/list/province/{province_id}/city/{city_id}`

#### Parameter

pathValue `province_id` 省id

pathValue `city_id` 市id

#### Return

```
{
    "count": 2,
    "next": null,
    "previous": null,
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
            "location": "北京朝阳区堆场",
            "latitude": "39.92111",
            "longitude": "116.46111",
            "site_code": "BJ001",
            "province": 1,
            "nation": 1
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
            "location": "北京海淀区堆场",
            "latitude": "39.92222",
            "longitude": "116.46222",
            "site_code": "BJ002",
            "province": 1,
            "nation": 1
        }
    ]
}
```

### 堆场详情查询



#### URL

`api/v1/cloudbox/rentservice/site/detail/{site_id}`

#### METHOD

`GET`

#### Parameter

pathValue `site_id` 获取仓库的详情，同时获取该仓库各种类型箱子的可用量

#### Return
```
{
    "message": "Success",
    "code": "000000",
    "data": {
        "box_counts": [
            {
                "box_num": 2,
                "box_type": {
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
                }
            },
            {
                "box_num": 2,
                "box_type": {
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
                }
            },
            {
                "box_num": 2,
                "box_type": {
                    "id": 3,
                    "box_type_name": "医药箱",
                    "box_type_detail": "",
                    "interval_time": 30,
                    "temperature_threshold_min": 2,
                    "temperature_threshold_max": 25,
                    "humidity_threshold_min": 0,
                    "humidity_threshold_max": 30,
                    "collision_threshold_min": 0,
                    "collision_threshold_max": 100,
                    "battery_threshold_min": 0,
                    "battery_threshold_max": 100,
                    "operation_threshold_min": 0,
                    "operation_threshold_max": 100,
                    "price": 30,
                    "length": 11,
                    "width": 1.2,
                    "height": 0.8
                }
            },
            {
                "box_num": 0,
                "box_type": {
                    "id": 4,
                    "box_type_name": "普通箱",
                    "box_type_detail": "",
                    "interval_time": 30,
                    "temperature_threshold_min": 2,
                    "temperature_threshold_max": 8,
                    "humidity_threshold_min": 0,
                    "humidity_threshold_max": 30,
                    "collision_threshold_min": 0,
                    "collision_threshold_max": 100,
                    "battery_threshold_min": 0,
                    "battery_threshold_max": 100,
                    "operation_threshold_min": 0,
                    "operation_threshold_max": 100,
                    "price": 50,
                    "length": 11,
                    "width": 1.2,
                    "height": 0.8
                }
            },
            {
                "box_num": 0,
                "box_type": {
                    "id": 5,
                    "box_type_name": "特殊箱",
                    "box_type_detail": "",
                    "interval_time": 30,
                    "temperature_threshold_min": -30,
                    "temperature_threshold_max": 50,
                    "humidity_threshold_min": 0,
                    "humidity_threshold_max": 30,
                    "collision_threshold_min": 0,
                    "collision_threshold_max": 100,
                    "battery_threshold_min": 0,
                    "battery_threshold_max": 100,
                    "operation_threshold_min": 0,
                    "operation_threshold_max": 100,
                    "price": 15,
                    "length": 11,
                    "width": 1.2,
                    "height": 0.8
                }
            }
        ],
        "site_info": {
            "id": 14,
            "city": {
                "id": 308,
                "city_name": "西安",
                "state_name": "陕西",
                "nation_name": "中国",
                "longitude": "108.93977",
                "latitude": "34.341574",
                "area_name": "亚洲",
                "culture": "",
                "taboo": "",
                "picture_url": "",
                "sorted_key": "x",
                "flag": 0,
                "nation": 1,
                "province": 27
            },
            "location": "西安堆场",
            "latitude": "34.211539",
            "longitude": "108.838780",
            "site_code": "XA001",
            "province": 27,
            "nation": 1
        }
    }
}
```


## 云箱订单查询API

### 承运人查询在运云箱

#### METHOD

`GET`

#### URL

`container/api/v1/cloudbox/rentservice/userinfo/list/{user_id}/process/`

#### Parameter

pathValue `user_id` 承运方用户id

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "count": 2,
        "limit": 10,
        "results": [
            {
                "lease_info_id": "111111",
                "box": {
                    "deviceid": "HNAR0000003",
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
                    "date_of_production": "1505786038000",
                    "carrier": 1,
                    "tid": "123",
                    "ava_flag": "Y",
                    "manufacturer": null,
                    "produce_area": null,
                    "hardware": null,
                    "battery": null,
                    "siteinfo": 1
                },
                "lease_start_time": "2017-10-10T00:00:00Z",
                "lease_end_time": null,
                "rent": 0,
                "user_id": "8c20d6d8-bde3-11e7-888f-525400d25920",
                "lease_admin_off": null,
                "lease_admin_on": null,
                "off_site": 1,
                "on_site": null
            },
            {
                "lease_info_id": "123123",
                "box": {
                    "deviceid": "HNAR0000001",
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
                    "date_of_production": "1505786038000",
                    "carrier": 1,
                    "tid": "123",
                    "ava_flag": "Y",
                    "manufacturer": null,
                    "produce_area": null,
                    "hardware": null,
                    "battery": null,
                    "siteinfo": 1
                },
                "lease_start_time": "2017-10-10T00:00:00Z",
                "lease_end_time": null,
                "rent": 0,
                "user_id": "8c20d6d8-bde3-11e7-888f-525400d25920",
                "lease_admin_off": null,
                "lease_admin_on": null,
                "off_site": 1,
                "on_site": null
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

### 承运人已完成订单list

#### METHOD

`GET`

#### URL

`container/api/v1/cloudbox/rentservice/userinfo/list/{user_id}/finished/`

#### Parameter

pathValue `user_id` 承运用户id

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "count": 2,
        "limit": 10,
        "results": [
            {
                "lease_info_id": "333333",
                "box": {
                    "deviceid": "HNAR0000005",
                    "type": {
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
                    },
                    "date_of_production": "1505786038000",
                    "carrier": 1,
                    "tid": "123",
                    "ava_flag": "Y",
                    "manufacturer": null,
                    "produce_area": null,
                    "hardware": null,
                    "battery": null,
                    "siteinfo": 1
                },
                "lease_start_time": "2017-10-10T00:00:00Z",
                "lease_end_time": "2017-12-12T00:00:00Z",
                "rent": 0,
                "user_id": "8c20d6d8-bde3-11e7-888f-525400d25920",
                "lease_admin_off": null,
                "lease_admin_on": null,
                "off_site": 1,
                "on_site": 14
            },
            {
                "lease_info_id": "222222",
                "box": {
                    "deviceid": "HNAR0000004",
                    "type": {
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
                    },
                    "date_of_production": "1505786038000",
                    "carrier": 1,
                    "tid": "123",
                    "ava_flag": "Y",
                    "manufacturer": null,
                    "produce_area": null,
                    "hardware": null,
                    "battery": null,
                    "siteinfo": 1
                },
                "lease_start_time": "2017-10-10T00:00:00Z",
                "lease_end_time": "2017-12-12T00:00:00Z",
                "rent": 0,
                "user_id": "8c20d6d8-bde3-11e7-888f-525400d25920",
                "lease_admin_off": null,
                "lease_admin_on": null,
                "off_site": 1,
                "on_site": 14
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
### 企业查询在运箱子订单list

#### METHOD

`GET`

#### URL

`container/api/v1/cloudbox/rentservice/enterlease/list/{enterprise_id}/process`

#### Parameter

pathValue `enterprise_id` 企业id

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "count": 2,
        "limit": 10,
        "results": [
            {
                "lease_info_id": "111111",
                "box": {
                    "deviceid": "HNAR0000003",
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
                    "date_of_production": "1505786038000",
                    "carrier": 1,
                    "tid": "123",
                    "ava_flag": "Y",
                    "manufacturer": null,
                    "produce_area": null,
                    "hardware": null,
                    "battery": null,
                    "siteinfo": 1
                },
                "on_site": null,
                "off_site": {
                    "id": 1,
                    "location": "北京朝阳区堆场",
                    "latitude": "39.92111",
                    "longitude": "116.46111",
                    "site_code": "BJ001",
                    "volume": 0,
                    "city": 1,
                    "province": 1,
                    "nation": 1
                },
                "lease_start_time": "2017-10-10T00:00:00Z",
                "lease_end_time": null,
                "rent": 0,
                "user_id": "8c20d6d8-bde3-11e7-888f-525400d25920",
                "lease_admin_off": null,
                "lease_admin_on": null
            },
            {
                "lease_info_id": "123123",
                "box": {
                    "deviceid": "HNAR0000001",
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
                    "date_of_production": "1505786038000",
                    "carrier": 1,
                    "tid": "123",
                    "ava_flag": "Y",
                    "manufacturer": null,
                    "produce_area": null,
                    "hardware": null,
                    "battery": null,
                    "siteinfo": 1
                },
                "on_site": null,
                "off_site": {
                    "id": 1,
                    "location": "北京朝阳区堆场",
                    "latitude": "39.92111",
                    "longitude": "116.46111",
                    "site_code": "BJ001",
                    "volume": 0,
                    "city": 1,
                    "province": 1,
                    "nation": 1
                },
                "lease_start_time": "2017-10-10T00:00:00Z",
                "lease_end_time": null,
                "rent": 0,
                "user_id": "8c20d6d8-bde3-11e7-888f-525400d25920",
                "lease_admin_off": null,
                "lease_admin_on": null
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
### 企业查询箱子已完成订单list

#### METHOD

`GET`

#### URL

`container/api/v1/cloudbox/rentservice/enterlease/list/{enterprise_id}/finished`

#### Parameter

pathValue `enterprise_id` 企业id

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "count": 2,
        "limit": 10,
        "results": [
            {
                "lease_info_id": "111111",
                "box": {
                    "deviceid": "HNAR0000003",
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
                    "date_of_production": "1505786038000",
                    "carrier": 1,
                    "tid": "123",
                    "ava_flag": "Y",
                    "manufacturer": null,
                    "produce_area": null,
                    "hardware": null,
                    "battery": null,
                    "siteinfo": 1
                },
                "on_site": null,
                "off_site": {
                    "id": 1,
                    "location": "北京朝阳区堆场",
                    "latitude": "39.92111",
                    "longitude": "116.46111",
                    "site_code": "BJ001",
                    "volume": 0,
                    "city": 1,
                    "province": 1,
                    "nation": 1
                },
                "lease_start_time": "2017-10-10T00:00:00Z",
                "lease_end_time": null,
                "rent": 0,
                "user_id": "8c20d6d8-bde3-11e7-888f-525400d25920",
                "lease_admin_off": null,
                "lease_admin_on": null
            },
            {
                "lease_info_id": "123123",
                "box": {
                    "deviceid": "HNAR0000001",
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
                    "date_of_production": "1505786038000",
                    "carrier": 1,
                    "tid": "123",
                    "ava_flag": "Y",
                    "manufacturer": null,
                    "produce_area": null,
                    "hardware": null,
                    "battery": null,
                    "siteinfo": 1
                },
                "on_site": null,
                "off_site": {
                    "id": 1,
                    "location": "北京朝阳区堆场",
                    "latitude": "39.92111",
                    "longitude": "116.46111",
                    "site_code": "BJ001",
                    "volume": 0,
                    "city": 1,
                    "province": 1,
                    "nation": 1
                },
                "lease_start_time": "2017-10-10T00:00:00Z",
                "lease_end_time": null,
                "rent": 0,
                "user_id": "8c20d6d8-bde3-11e7-888f-525400d25920",
                "lease_admin_off": null,
                "lease_admin_on": null
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

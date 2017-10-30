## 云箱类型API

### 云箱类型查询

#### METHOD

`GET`

#### URL

`container/api/v1/cloudbox/rentservice/boxtype/list`

#### Parameter

无

#### Return

```
{
    "message": "Success",
    "code": "000000",
    "data": [
        {
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
        {
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
        {
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
        {
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
        },
        {
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
    ]
}
```




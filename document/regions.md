## 省市区接口

### 省列表查询

### METHOD

`GET`

#### URL

`container/api/v1/cloudbox/rentservice/regions/provinces`

#### Parameter

无

#### Return

```
{
    "message": "Success",
    "code": "000000",
    "data": [
        {
            "province_id": 1,
            "province_name": "北京市",
            "zip_code": "110000",
            "nation": 1
        },
        {
            "province_id": 2,
            "province_name": "天津市",
            "zip_code": "120000",
            "nation": 1
        },
        {
            "province_id": 3,
            "province_name": "河北省",
            "zip_code": "130000",
            "nation": 1
        },
        {
            "province_id": 4,
            "province_name": "山西省",
            "zip_code": "140000",
            "nation": 1
        },
        {
            "province_id": 5,
            "province_name": "内蒙古自治区",
            "zip_code": "150000",
            "nation": 1
        },
        {
            "province_id": 6,
            "province_name": "辽宁省",
            "zip_code": "210000",
            "nation": 1
        },
        {
            "province_id": 7,
            "province_name": "吉林省",
            "zip_code": "220000",
            "nation": 1
        },
        {
            "province_id": 8,
            "province_name": "黑龙江省",
            "zip_code": "230000",
            "nation": 1
        },
        {
            "province_id": 9,
            "province_name": "上海市",
            "zip_code": "310000",
            "nation": 1
        },
        {
            "province_id": 10,
            "province_name": "江苏省",
            "zip_code": "320000",
            "nation": 1
        },
        {
            "province_id": 11,
            "province_name": "浙江省",
            "zip_code": "330000",
            "nation": 1
        },
        {
            "province_id": 12,
            "province_name": "安徽省",
            "zip_code": "340000",
            "nation": 1
        },
        {
            "province_id": 13,
            "province_name": "福建省",
            "zip_code": "350000",
            "nation": 1
        },
        {
            "province_id": 14,
            "province_name": "江西省",
            "zip_code": "360000",
            "nation": 1
        },
        {
            "province_id": 15,
            "province_name": "山东省",
            "zip_code": "370000",
            "nation": 1
        },
        {
            "province_id": 16,
            "province_name": "河南省",
            "zip_code": "410000",
            "nation": 1
        },
        {
            "province_id": 17,
            "province_name": "湖北省",
            "zip_code": "420000",
            "nation": 1
        },
        {
            "province_id": 18,
            "province_name": "湖南省",
            "zip_code": "430000",
            "nation": 1
        },
        {
            "province_id": 19,
            "province_name": "广东省",
            "zip_code": "440000",
            "nation": 1
        },
        {
            "province_id": 20,
            "province_name": "广西壮族自治区",
            "zip_code": "450000",
            "nation": 1
        },
        {
            "province_id": 21,
            "province_name": "海南省",
            "zip_code": "460000",
            "nation": 1
        },
        {
            "province_id": 22,
            "province_name": "重庆市",
            "zip_code": "500000",
            "nation": 1
        },
        {
            "province_id": 23,
            "province_name": "四川省",
            "zip_code": "510000",
            "nation": 1
        },
        {
            "province_id": 24,
            "province_name": "贵州省",
            "zip_code": "520000",
            "nation": 1
        },
        {
            "province_id": 25,
            "province_name": "云南省",
            "zip_code": "530000",
            "nation": 1
        },
        {
            "province_id": 26,
            "province_name": "西藏自治区",
            "zip_code": "540000",
            "nation": 1
        },
        {
            "province_id": 27,
            "province_name": "陕西省",
            "zip_code": "610000",
            "nation": 1
        },
        {
            "province_id": 28,
            "province_name": "甘肃省",
            "zip_code": "620000",
            "nation": 1
        },
        {
            "province_id": 29,
            "province_name": "青海省",
            "zip_code": "630000",
            "nation": 1
        },
        {
            "province_id": 30,
            "province_name": "宁夏回族自治区",
            "zip_code": "640000",
            "nation": 1
        },
        {
            "province_id": 31,
            "province_name": "新疆维吾尔自治区",
            "zip_code": "650000",
            "nation": 1
        },
        {
            "province_id": 32,
            "province_name": "台湾省",
            "zip_code": "710000",
            "nation": 1
        },
        {
            "province_id": 33,
            "province_name": "香港特别行政区",
            "zip_code": "810000",
            "nation": 1
        },
        {
            "province_id": 34,
            "province_name": "澳门特别行政区",
            "zip_code": "820000",
            "nation": 1
        }
    ]
}
```

### 指定省的市列表

#### URL

`container/api/v1/cloudbox/rentservice/regions/cities/{province_id}`

#### Parameter

pathValue `province_id`

#### Return

```
{
    "message": "Success",
    "code": "000000",
    "data": [
        {
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
        {
            "id": 309,
            "city_name": "铜川",
            "state_name": "陕西",
            "nation_name": "中国",
            "longitude": "108.945019",
            "latitude": "34.897887",
            "area_name": "亚洲",
            "culture": "",
            "taboo": "",
            "picture_url": "",
            "sorted_key": "t",
            "flag": 0,
            "nation": 1,
            "province": 27
        },
        {
            "id": 310,
            "city_name": "宝鸡",
            "state_name": "陕西",
            "nation_name": "中国",
            "longitude": "107.237743",
            "latitude": "34.363184",
            "area_name": "亚洲",
            "culture": "",
            "taboo": "",
            "picture_url": "",
            "sorted_key": "b",
            "flag": 0,
            "nation": 1,
            "province": 27
        },
        {
            "id": 311,
            "city_name": "咸阳",
            "state_name": "陕西",
            "nation_name": "中国",
            "longitude": "108.708991",
            "latitude": "34.329605",
            "area_name": "亚洲",
            "culture": "",
            "taboo": "",
            "picture_url": "",
            "sorted_key": "x",
            "flag": 0,
            "nation": 1,
            "province": 27
        },
        {
            "id": 312,
            "city_name": "渭南",
            "state_name": "陕西",
            "nation_name": "中国",
            "longitude": "109.502882",
            "latitude": "34.49938",
            "area_name": "亚洲",
            "culture": "",
            "taboo": "",
            "picture_url": "",
            "sorted_key": "w",
            "flag": 0,
            "nation": 1,
            "province": 27
        },
        {
            "id": 313,
            "city_name": "延安",
            "state_name": "陕西",
            "nation_name": "中国",
            "longitude": "109.489757",
            "latitude": "36.585445",
            "area_name": "亚洲",
            "culture": "",
            "taboo": "",
            "picture_url": "",
            "sorted_key": "y",
            "flag": 0,
            "nation": 1,
            "province": 27
        },
        {
            "id": 314,
            "city_name": "汉中",
            "state_name": "陕西",
            "nation_name": "中国",
            "longitude": "107.023323",
            "latitude": "33.06748",
            "area_name": "亚洲",
            "culture": "",
            "taboo": "",
            "picture_url": "",
            "sorted_key": "h",
            "flag": 0,
            "nation": 1,
            "province": 27
        },
        {
            "id": 315,
            "city_name": "榆林",
            "state_name": "陕西",
            "nation_name": "中国",
            "longitude": "109.734589",
            "latitude": "38.28539",
            "area_name": "亚洲",
            "culture": "",
            "taboo": "",
            "picture_url": "",
            "sorted_key": "y",
            "flag": 0,
            "nation": 1,
            "province": 27
        },
        {
            "id": 316,
            "city_name": "安康",
            "state_name": "陕西",
            "nation_name": "中国",
            "longitude": "109.029022",
            "latitude": "32.684714",
            "area_name": "亚洲",
            "culture": "",
            "taboo": "",
            "picture_url": "",
            "sorted_key": "a",
            "flag": 0,
            "nation": 1,
            "province": 27
        },
        {
            "id": 317,
            "city_name": "商洛",
            "state_name": "陕西",
            "nation_name": "中国",
            "longitude": "109.940477",
            "latitude": "33.870422",
            "area_name": "亚洲",
            "culture": "",
            "taboo": "",
            "picture_url": "",
            "sorted_key": "s",
            "flag": 0,
            "nation": 1,
            "province": 27
        }
    ]
}
```

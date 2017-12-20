## 相关API


### 1. 登录海航云箱运营平台
#### 方法
`POST`

#### URL

`106.2.20.186/container/api/v1/cloudbox/monservice/auth`

#### Parameter

```
{"username": "huaren", "password": "38f4a7cbe7254326f4847422ea4bfdd4", "timestamp": 1513586931}

说明
1. username  用户名
2. password  加密密码，为 md5(md5(明文password) + timestamp)，字母全小写
3. timestamp 系统当前时间戳，例如1483200000代表：2017-01-01 00:00:00
4. 目前给华人分配的用户名和密码为：huaren / @Huaren1234

```

#### Return

```
{
    "token": "ee43908f-d4cb-11e7-86a0-6a00027160c0",
    "role": "carrier"
}
```




### 2. 登出
#### 方法
`POST`

#### URL

`106.2.20.186/container/api/v1/cloudbox/monservice/logout`

#### Header

```
Authorization: 登录时运营平台返回的token

```

#### Return

```
{
    "msg": "退出成功"
}
```


### 3. 云箱数据查询
#### 方法
`POST`

#### URL

`106.2.20.186/container/api/v1/cloudbox/monservice/getHuarenData?limit=10&offset=0`

#### Header

```
Authorization: 登录时运营平台返回的token

```

#### Parameter

```
{"starttime": 1513296000, "endtime": 1513299600, "deviceids": ["01-03-17-09-00-20", "01-03-17-09-00-24"]}

说明
1. starttime  要查询数据的开始时间
2. endtime    要查询数据的结束时间
3. deviceids  要查询的箱子id数组

```

#### Return

```
{
    "message": "query data success",
    "code": "OK",
    "data": {
        "count": 65,
        "limit": 10,
        "results": [
            {
                "timestamp": 1513296029,
                "deviceid": "01-03-17-09-00-20",
                "temperature": "22.2",
                "humidity": "18.1",
                "longitude": "108.8354",
                "latitude": "34.212492",
                "speed": "0.0",
                "collide": "0",
                "light": "0"
            },
            
						......
                        
            {
                "timestamp": 1513298729,
                "deviceid": "01-03-17-09-00-20",
                "temperature": "22.2",
                "humidity": "18.6",
                "longitude": "108.8354",
                "latitude": "34.212492",
                "speed": "0.0",
                "collide": "0",
                "light": "0"
            }
        ],
        "links": {
            "previous": null,
            "next": "http://127.0.0.1:8000/container/api/v1/cloudbox/monservice/getHuarenData?limit=10&offset=10"
        },
        "offset": 0
    }
}
```

#### 说明

```
limit：每页返回条数
offset：偏移量，要获取数据的开始位置
deviceids参数可以不传，如果不传则查询指定的云箱，如果传了则查询对应的箱子
返回数据中包括总条数、每页条数、上一页、下一页查询链接。
```


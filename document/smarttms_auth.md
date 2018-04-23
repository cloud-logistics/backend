## 用户认证接口
### 重置密码接口
#### 方法
`POST`

#### URL

`api/v1/cloudbox/auth/pwdreset`

#### Parameter

```
orig_password: md5(md5(orig_password_raw)+timestamp)
new_password:md5(password_raw)
timestamp:加密时的utc时间戳


{
    "user_id": "0b922f14-d00b-11e7-aafd-525400bbac8e",
    "orig_password":"00b945c1fd92aa2623b704d8d37d8ffc",
    "new_password":"199db40c253bdc3875400e8ac67b9e21",
    "timestamp":1511839692
}
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "user_id": "0b922f14-d00b-11e7-aafd-525400bbac8e",
        "user_name": "dddddd",
        "register_time": "2017-11-23T04:59:11.544126Z",
        "status": "",
        "avatar_url": "",
        "user_phone": "12312312312",
        "user_email": "",
        "user_token": "dbf15a70056b49feaa394288ea9299e3",
        "role": "user",
        "user_real_name": "fff",
        "user_gender": "男",
        "user_nickname": "",
        "user_alias_id": "0b9314d8d00b11e7aafd525400bbac8e",
        "enterprise": "e8d3bc38-beb0-11e7-888f-525400d25920",
        "group": "rentuser"
    }
}
```
####说明
```
该方法无需携带token，请求前确保用户已存在
```
### 用户登录认证接口（app）
#### 方法
`POST`

#### URL

`api/v1/cloudbox/smarttms/auth/authsalt`

#### Parameter

```
password: md5(md5(password_raw)+timestamp)
username: 登陆用户名
timestamp:加密时的utc时间戳


{
    "username": "test",
    "password":"00b945c1fd92aa2623b704d8d37d8ffc",
    "timestamp":1511839692
}
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "user_id": "0b922f14-d00b-11e7-aafd-525400bbac8e",
        "user_name": "dddddd",
        "register_time": "2017-11-23T04:59:11.544126Z",
        "status": "",
        "avatar_url": "",
        "user_phone": "12312312312",
        "user_email": "",
        "user_token": "dbf15a70056b49feaa394288ea9299e3",
        "role": "user",
        "user_real_name": "fff",
        "user_gender": "男",
        "user_nickname": "",
        "user_alias_id": "0b9314d8d00b11e7aafd525400bbac8e",
        "enterprise": "e8d3bc38-beb0-11e7-888f-525400d25920",
        "group": "rentuser"
    }
}
```
####说明
```
该方法无需携带token，请求前确保用户已存在
```
### 运营平台登出接口
#### 方法
`POST`

#### URL

`api/v1/cloudbox/smarttms/logout`

#### Header

```
Authorization: 139a2d1c6f0a44909670f4e749a1397d
```

#### Return

```
{
    "msg": "退出成功"
}

```





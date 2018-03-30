## TMS用户相接口

### 查询用户列表
#### 方法
`GET`

#### URL

`container/api/v1/cloudbox/tms/user/userslist/(?P<role_id>[0-9a-zA-Z-]+)`

#### Parameter

```
role_id
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "count": 1,
        "limit": 10,
        "results": [
            {
                "user_id": "4",
                "user_name": "admin",
                "register_time": "2018-03-20T14:00:02.412827+08:00",
                "status": "1",
                "avatar_url": "1",
                "user_phone": "1",
                "user_email": "1@hna",
                "user_token": "9665f7452bec11e8b2256a00027160c0",
                "user_real_name": "",
                "user_gender": "",
                "user_nickname": "",
                "user_alias_id": "",
                "role": "1",
                "group": "817ec9cf-28e4-11e8-8873-6a00027160c0"
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
####说明
```
该方法需携带token，请求前确保用户已存在
```
### 获取用户详细信息
#### 方法
`GET`

#### URL

`container/api/v1/cloudbox/tms/user/userdetail/(?P<user_id>[0-9a-zA-Z-]+)`

#### Parameter

```
user_id用户id
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "user_id": "4",
        "user_name": "admin",
        "register_time": "2018-03-20T14:00:02.412827+08:00",
        "status": "1",
        "avatar_url": "1",
        "user_phone": "1",
        "user_email": "1@hna",
        "user_token": "9665f7452bec11e8b2256a00027160c0",
        "user_real_name": "",
        "user_gender": "",
        "user_nickname": "",
        "user_alias_id": "",
        "role": "1",
        "group": "817ec9cf-28e4-11e8-8873-6a00027160c0"
    }
}
```
####说明
```
该方法需携带token，请求前确保用户已存在
```
### 增加用户
#### 方法
`POST`

#### URL

`container/api/v1/cloudbox/tms/user/adduser`

#### Parameter

```
{
    "user_name": "fishman05",
    "user_real_name":"spider",
    "user_gender":"Male",
    "user_phone":"18012341234",
    "role":"2"
}
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "user_id": "2a9467f0-2ceb-11e8-aafd-525400bbac8e"
    }
}
```
####说明
```
该方法需携带token，请求前确保用户已存在
```
### 删除用户
#### 方法
`DELETE`

#### URL

`container/api/v1/cloudbox/tms/user/rmuser/(?P<user_id>[0-9a-zA-Z-]+)/`

#### Parameter

```
无
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "user_id": "2a9467f0-2ceb-11e8-aafd-525400bbac8e"
    }
}
```
####说明
```
该方法需携带token，请求前确保用户已存在
```
### 修改用户
#### 方法
`POST`

#### URL

`container/api/v1/cloudbox/tms/user/update`

#### Parameter

```
{
    "user_id": "01a56814-2da2-11e8-aafd-525400bbac8e",
    "user_gender":"女",
    "user_nickname":"jane",
    "user_phone":12345678,
    "user_email":"123@hnair.com"
}
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "user_id": "01a56814-2da2-11e8-aafd-525400bbac8e"
    }
}
```
####说明
```
该方法需携带token，请求前确保用户已存在
```
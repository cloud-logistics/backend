## TMS用户登录接口

### 管理员加密登录接口
#### 方法
`POST`

#### URL

`container/api/v1/cloudbox/tms/auth/adminauthsalt`

#### Parameter

```
{
   "username":"mark",
   "password":"hna123",
   "timestamp":1521515662
}
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
        "group": "admin"
    }
}
```
####说明
```
该方法需携带token，请求前确保用户已存在,password是已经md5加密过的密码
```
### 用户加密登录接口
#### 方法
`POST`

#### URL

`container/api/v1/cloudbox/tms/auth/authsalt`

#### Parameter

```
{
   "username":"mark",
   "password":"hna123",
   "timestamp":1521515662
}
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
        "group": "admin"
    }
}
```
####说明
```
该方法需携带token，请求前确保用户已存在,password是已经md5加密过的密码
```
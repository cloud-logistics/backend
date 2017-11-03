## 企业用户接口

### 添加企业用户
#### 方法
`POST`

#### URL

`container／api/v1/cloudbox/rentservice/enterpriseuser/addenterpriseuser／`

#### Parameter

```
{
    "user_name": "mark4",
    "user_password": "123456",
    "avatar_url": "http://www.xxx.com",
    "user_phone": "18011112222",
    "user_email": "12345@qq.com",
    "enterprise_id": "32d78cee-bd35-11e7-a3f4-9801a7b3c9f3",
    "role":"admin",
    "group":"rentadmin"
}
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "user_id": "a68776e3-bd41-11e7-8cac-9801a7b3c9f3"
    }
}
```
####说明
```
1、该方法请求需要在header携带token
2、enterprise_id 企业用户信息id必须存在，group的定义必须存在
```
### 修改企业用户
#### 方法
`POST`

#### URL

`container／api/v1/cloudbox/rentservice/enterpriseuser/updateenterpriseuser／`

#### Parameter

```
{
    "user_name": "mark2",
    "user_password": "123456",
    "avatar_url": "http://www.xxx.com",
    "user_phone": "18011113332",
    "user_email": "test@qq.com",
    "enterprise_id": "32d78cee-bd35-11e7-a3f4-9801a7b3c9f3",
    "user_id":"ab4721cc-bd3f-11e7-b6a0-9801a7b3c9f3"
}
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "user_id": "ab4721cc-bd3f-11e7-b6a0-9801a7b3c9f3"
    }
}
```
####说明
```
1、该方法请求需要在header携带token
2、enterprise_id 企业用户信息id必须存在，user_id的定义必须存在
3、只允许修改参数里面的值，其他字段不能修改
```
### 删除企业用户
#### 方法
`DELETE`

#### URL

`container／api/v1/cloudbox/rentservice/enterpriseuser/{user_id}`

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
        "user_id": "50befae1-bd41-11e7-8352-9801a7b3c9f3"
    }
}
```
####说明
```
1、该方法请求需要在header携带token。
```
### 企业用户列表
#### 方法
`GET`

#### URL

`container／api/v1/cloudbox/rentservice/enterpriseuser/list`

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
        "count": 2,
        "num_pages": 1,
        "results": [
            {
                "user_id": "3ccf0bca-bf98-11e7-b3ec-9801a7b3c9f3",
                "user_name": "mark2",
                "user_password": "1234567",
                "register_time": "2017-11-02T06:37:03.422609Z",
                "status": "",
                "avatar_url": "http://www.xxx.com",
                "user_phone": "18011112222",
                "user_email": "12345@qq.com",
                "user_token": "58ba6f474e5844d093af285270e8f02a",
                "role": "admin",
                "enterprise": "dae79623-bea8-11e7-a2b6-9801a7b3c9f3",
                "group": "6bfa276b-ba23-11e7-87ef-9801a7b3c9f3"
            },
            {
                "user_id": "3e9a30b0-bf98-11e7-987e-9801a7b3c9f3",
                "user_name": "mark5",
                "user_password": "1234567",
                "register_time": "2017-11-02T06:37:06.431642Z",
                "status": "",
                "avatar_url": "http://www.xxx.com",
                "user_phone": "18011112222",
                "user_email": "12345@qq.com",
                "user_token": "13470786b77c43f0a767fbc414aff4ee",
                "role": "admin",
                "enterprise": "dae79623-bea8-11e7-a2b6-9801a7b3c9f3",
                "group": "6bfa276b-ba23-11e7-87ef-9801a7b3c9f3"
            }
        ],
        "links": {
            "previous": null,
            "next": null
        }
    }
}
```
####说明
```
1、该方法请求需要在header携带token。
2、该方法支持分页，格式如上
```
### 企业用户详情
#### 方法
`GET`

#### URL

`container／api/v1/cloudbox/rentservice/enterpriseuser/detail/{user_id}／`

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
        "user_id": "4ea892d4-bea9-11e7-bec2-9801a7b3c9f3",
        "user_name": "mark3",
        "user_password": "1234567",
        "register_time": "2017-11-01T02:06:43.651073Z",
        "status": "",
        "avatar_url": "http://www.xxx.com",
        "user_phone": "18011112222",
        "user_email": "12345@qq.com",
        "user_token": "80753ae4a01247a89d5a637046b47018",
        "role": "admin",
        "enterprise": "dae79623-bea8-11e7-a2b6-9801a7b3c9f3",
        "group": "6bfa276b-ba23-11e7-87ef-9801a7b3c9f3"
    }
}
```
####说明
```
1、该方法请求需要在header携带token。
2、该方法支持分页，格式如上
```
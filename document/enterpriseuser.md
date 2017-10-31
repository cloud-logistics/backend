## 企业用户接口

### 添加企业用户
#### 方法
`POST`

#### URL

`api/v1/cloudbox/rentservice/enterpriseuser/addenterpriseuser`

#### Parameter

```
{
    "username": "mark4",
    "password": "123456",
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

`api/v1/cloudbox/rentservice/enterpriseuser/updateenterpriseuser`

#### Parameter

```
{
    "username": "mark2",
    "password": "123456",
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

`api/v1/cloudbox/rentservice/enterpriseuser/{user_id}`

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
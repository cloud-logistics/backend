## 用户认证接口

### 认证用户并获取用户访问token和所属用户群组
#### 方法
`POST`

#### URL

`api/v1/cloudbox/auth/auth`

#### Parameter

```
{
   "username":"mark",
   "password":"hna123"
}
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "user_token": "5f12dba2d8a54e2a82873e5bfc60e020",
        "group": "admin"
    }
}
```
####说明
```
该方法无需携带token，请求前确保用户已存在
```

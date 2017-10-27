## 企业信息相关接口

### 添加租赁企业信息
#### 方法
`POST`

#### URL

`api/v1/cloudbox/rentservice/enterprise/enterpriseinfo/addenterpriseinfo`

#### Parameter

```
{
	"enterprise_name":"海航科技",
	"enterprise_tele":"02988881111",
	"enterprise_license_id":"123456789",
	"enterprise_legal_rep_name":"mark1",
	"enterprise_deposit":"20002",
	"enterprise_email":"mark@hnair.com",
	"enterprise_license_id_url":"http://www.xxx.com",
}
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "enterprise_id": "74ccaf72-babc-11e7-888f-525400d25920"
    }
}
```
####说明
```
该方法请求需要在header携带token
```
### 修改租赁企业信息
#### 方法
`POST`

#### URL

`api/v1/cloudbox/rentservice/enterprise/enterpriseinfo/updateenterpriseinfo`

#### Parameter

```
{
	"enterprise_id":"20caf54c-b96c-11e7-b9ff-9801a7b3c9f3",
	"enterprise_name":"海航科技",
	"enterprise_tele":"02988881111",
	"enterprise_license_id":"123456789",
	"enterprise_legal_rep_name":"mark1",
	"enterprise_deposit":"20002",
	"enterprise_email":"mark@hnair.com",
	"enterprise_license_id_url":"http://www.xxx.com",
}
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "enterprise_id": "2dbd6670-babd-11e7-888f-525400d25920"
    }
}
```
####说明
```
该方法请求需要在header携带token，必须携带请求参数的所有key，否则会报错。
```
### 删除租赁企业信息
#### 方法
`DELETE`

#### URL

`api/v1/cloudbox/rentservice/enterprise/enterpriseinfo/{enterprise_id}`

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
        "enterprise_id": "2dbd6670-babd-11e7-888f-525400d25920"
    }
}
```
####说明
```
该方法请求需要在header携带token。
```
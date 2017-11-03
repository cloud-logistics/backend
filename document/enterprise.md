## 企业信息相关接口

### 添加租赁企业信息
#### 方法
`POST`

#### URL

`container／api/v1/cloudbox/rentservice/enterprise/enterpriseinfo/addenterpriseinfo/`

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

`container／api/v1/cloudbox/rentservice/enterprise/enterpriseinfo/updateenterpriseinfo/`

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

`container／api/v1/cloudbox/rentservice/enterprise/enterpriseinfo/{enterprise_id}`

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
###查询租赁企业信息列表
#### 方法
`GET`

#### URL

`container／api/v1/cloudbox/rentservice/enterprise/enterpriseinfo/list`

#### Parameter

```
无
```

#### Return

```
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "enterprise_id": "4c4a4d5a-bde3-11e7-888f-525400d25920",
            "enterprise_name": "阿里巴巴",
            "enterprise_tele": "02988881111",
            "enterprise_license_id": "123456789",
            "enterprise_license_id_url": "http://www.taobao.com",
            "enterprise_legal_rep_name": "mark1",
            "enterprise_email": "mark@hnair.com",
            "enterprise_deposit": 20002,
            "enterprise_deposit_status": 0,
            "enterprise_address": "",
            "enterprise_homepage_url": "",
            "register_time": "2017-10-31T02:29:19.325607Z"
        }
    ]
}
```
####说明
```
该方法请求需要在header携带token, 此方法可分页
```
###查询租赁企业信息
#### 方法
`GET`

#### URL

`container／api/v1/cloudbox/rentservice/enterprise/enterpriseinfo/detail/{enterprise_id}/`

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
        "enterprise_id": "4c4a4d5a-bde3-11e7-888f-525400d25920",
        "enterprise_name": "阿里巴巴",
        "enterprise_tele": "02988881111",
        "enterprise_license_id": "123456789",
        "enterprise_license_id_url": "http://www.taobao.com",
        "enterprise_legal_rep_name": "mark1",
        "enterprise_email": "mark@hnair.com",
        "enterprise_deposit": 20002,
        "enterprise_deposit_status": 0,
        "enterprise_address": "",
        "enterprise_homepage_url": "",
        "register_time": "2017-10-31T02:29:19.325607Z"
    }
}
```
####说明
```
该方法请求需要在header携带token
```
###企业租金确认
#### 方法
`PUT`

#### URL

`container／rentservice/enterprise/enterpriseinfo/depositconfirm`

#### Parameter

```
{
    "enterprise_id": "1ea0e88f-bea9-11e7-88fa-9801a7b3c9f3"
}
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "enterprise_id": "dae79623-bea8-11e7-a2b6-9801a7b3c9f3",
        "enterprise_name": "阿里巴巴",
        "enterprise_tele": "02988881111",
        "enterprise_license_id": "1234567890",
        "enterprise_license_id_url": "http://www.baidu.com",
        "enterprise_legal_rep_name": "mark1",
        "enterprise_email": "mark@hnair.com",
        "enterprise_deposit": 20002,
        "enterprise_deposit_status": 1,
        "enterprise_address": "",
        "enterprise_homepage_url": "",
        "register_time": "2017-11-01T02:03:29.454933Z"
    }
}
```
####说明
```
该方法请求需要在header携带token
```
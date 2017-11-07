## 云箱租赁和归还相关接口

### 云箱租赁接口
#### 方法
`POST`

#### URL

`container／api/v1/cloudbox/rentservice/boxrentservice/createorder`

#### Parameter

```
{
	"site_id":"14",
	"appoint_id":"00872106-c052-11e7-888f-525400d25920",
	"box_id_list":["HNAF0000284", "HNAR0000247"]
}
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "rent_lease_info_id_list": [
            "35f35be8-c390-11e7-888f-525400d25920",
            "35f66fa4-c390-11e7-888f-525400d25920"
        ]
    }
}
```
####说明
```
该方法请求需要在header携带token
```
### 归还云箱接口
#### 方法
`POST`

#### URL

`container/api/v1/cloudbox/rentservice/boxrentservice/finishorder`

#### Parameter

```
{
	"site_id":"14",
	"box_id_list":["HNAF0000284", "HNAR0000247"]
}
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "rent_lease_info_id_list": [
            "35f35be8-c390-11e7-888f-525400d25920",
            "35f66fa4-c390-11e7-888f-525400d25920"
        ]
    }
}
```
####说明
```
该方法请求需要在header携带token，必须携带请求参数的所有key，否则会报错。
此方法不可重复调用，调用一次后标志位置1
```
## 仓库API

### 1. 增加仓库

#### 方法：
 
`POST`

#### URL：

`container/api/v1/cloudbox/sites`

#### BODY:

```
 {
	"location": "西安堆场",
	"longitude": "120.0000",
	"latitude": "30.0000",
	"site_code": "",
	"volume": 500,
	"city_id": 1,
	"province_id": 1,
	"nation_id": 1
}
```

#### 响应：

```
{
    "status": "OK",
    "msg": "add site success"
}
```

```
{
    "status": "ERROR",
    "msg": "error msg"
}
```

### 2. 修改仓库：

#### URL：

`container/api/v1/cloudbox/sites/{site_id}`

#### 方法： 

`PUT`

#### BODY:

```
{
	"location": "测试666",
	"longitude": "120.00",
	"latitude": "30.00",
	"site_code": "",
	"volume": 500,
	"city_id": 1,
	"province_id": 1,
	"nation_id": 1
}
 ```
 
#### 返回：

```
{
    "status": "OK",
    "msg": "modify site success"
}
```


### 3. 删除仓库：

#### URL： 

`container/api/v1/cloudbox/sites/{site_id}`

#### 方法： 

`DELETE`

#### BODY:

`无`

#### 返回：
```
{
    "status": "OK",
    "msg": "delete site success"
}
```
## 渔场增删改API

### 1. 增加渔场

#### 方法：
 
`POST`

#### URL：

`container/api/v1/cloudbox/tms/fishery`

#### BODY:

```
{
    "latitude": "18.20000",
    "fishery_name": "三亚渔场",
    "longitude": "109.50000"
}

```


#### 响应：

```
{
    "status": "OK",
    "msg": "save fishery success."
}

```


### 2. 修改渔场：

#### URL：

`container/api/v1/cloudbox/tms/fishery/{fishery_id}`

#### 方法： 

`PUT`

#### BODY:

```
{
    "latitude": "18.20000",
    "fishery_name": "三亚渔场",
    "longitude": "109.50000"
}

```
 
#### 返回：

```
{
    "status": "OK",
    "msg": "update fishery success."
}
```


### 3. 删除渔场：

#### URL：

`container/api/v1/cloudbox/tms/fishery/{fishery_id}`

#### 方法： 

`DELETE`

#### BODY:

```
无

```
 
#### 返回：

```
{
    "status": "OK",
    "msg": "delete fishery success."
}
```
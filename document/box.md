## 云箱API

### 1. 增加云箱

#### 方法：
 
`POST`

#### URL：

`container/api/v1/cloudbox/basicInfoConfig`

#### BODY:

```
 {
    "rfid":"12345",
    "containerType":1,
    "factory":3,
    "factoryLocation":3,
    "batteryInfo":1,
    "hardwareInfo":1,
    "manufactureTime":"1509431998000"
 }
```

#### 响应：

```
{
    "status": "OK",
    "msg": "add box success"
}
```

```
{
    "status": "ERROR",
    "msg": "error msg"
}
```

### 2. 编辑云箱：

#### URL：

`container/api/v1/cloudbox/basicInfoMod`

#### 方法： 

`PUT`

#### BODY:

```
 {
    "containerId": "HNAR0000170",
    "rfid":"666",
    "containerType":1,
    "factory":3,
    "factoryLocation":3,
    "batteryInfo":1,
    "hardwareInfo":1,
    "manufactureTime":"1509431778000"
 }
 ```
 
#### 返回：

```
{
    "status": "OK",
    "msg": "modify box success"
}
```

### 3. 删除云箱：

#### URL： 

`container/api/v1/cloudbox/basicInfo/{container_id}`

#### 方法： DELETE

#### BODY:

`无`

#### 返回：
```
{
    "status": "OK",
    "msg": "delete box success"
}
```
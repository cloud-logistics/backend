## 传感器数据导出接口

### 导出数据查询接口
#### 方法
`GET`

#### URL

`106.2.20.186:8000/api/v1/cloudbox/getdata?day=2018-01-09`

#### Header

```
token a921a69a33ae461396167d112b813d90
```

#### Parameter

```
day  必须携带参数，要查询的天，每次只能查询一天，不能查询当天，形如：2018-01-09
```

#### Return

```
{
    "msg": "parameter is required",
    "code": "999999",
    "result": "False",
    "t": "{}"
}
```
或


```
{
    "msg": "Unauthorized",
    "code": "999999",
    "result": "False",
    "t": "{}"
}

```
或

```
返回application/octet-stream 可直接下载
```

####说明
```
导出数据默认在每天凌晨2点定时执行，所以只可以获取系统当前实际前一天之前的数据，包括前一天。
xxxxx/cloudbox/getdata?day=  day参数为空时默认查询前一天
请求响应正常时，返回.zip文件
```

####管理员接口
```
定时导出失败时，可以通过访问如下接口手动导出，参数说明同查询接口。
106.2.20.186:8000/api/v1/cloudbox/dumpdata?day=2018-01-09
```


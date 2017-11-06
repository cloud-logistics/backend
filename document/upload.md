## 上传接口

### 上传图片至七牛云接口
#### 方法
`PUT`

#### URL

`container/api/v1/cloudbox/rentservice/upload/{filename}`

#### Parameter

```
上传的附件，其他无
```

#### Return

```
{
    "message": "Succ",
    "code": "0000",
    "data": {
        "url": "oyzmceglk.bkt.clouddn.com/0cadc3e1-c2d5-11e7-8f9d-9801a7b3c9f3-hna1.jpeg",
        "hash": "FjmOaq1YJio2t0CreR9caiqAcTZR",
        "key": "0cadc3e1-c2d5-11e7-8f9d-9801a7b3c9f3-hna1.jpeg"
    }
}
```
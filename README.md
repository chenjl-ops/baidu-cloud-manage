# baidu-cloud-manage
---
```
主要实现百度云接口鉴权，密码加解密等
```

## 说明描述
---
```
#### baidu_base_config.py  主要提供 AccessKeyID 和 AccessKeySecret配置
1、从apollo获取配置
2、设置default配置

#### baidu_cloud_auth.py  主要提供百度签名服务类

#### baidu_api_manage.py  主要提供百度统一访问，百度密码加解密算法
1、提供统一的 http请求
2、提供百度passwd加解密算法

####go 版本验签使用方法
url := "https://billing.baidubce.com/v1/bill/resource/month?beginTime=%s&endTime=%s&productType=%s&pageNo=%d&pageSize=%d"
headers := map[string]string{
		"Host":         "billing.baidubce.com",
		"Content-Type": "application/json",
}
bc := baiducloud.NewBaiduCloud(fmt.Sprintf(url, startTime, endTime, v, 1, pageSize), headers, "GET")
err := bc.Request(data, &resultData)

```

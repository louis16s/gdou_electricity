# 电费查询

这个项目是一个用于查询广东海洋大学电费的脚本，获取电表信息并显示电费余额。\
 [ios-快捷指令-电费查询](https://www.icloud.com/shortcuts/6631445ecfd04095afdf0c08c487c185)
## 使用方法

1. 在代码中填写正确的参数：
   - `token`：访问令牌，用于身份验证。
   - `budingID`：楼栋ID，标识要查询的宿舍。
   - `comAddress`：电表地址，指定要查询的电表。
   - `token和budingID`的获取：登录[电费查询](https://cz.gdou.edu.cn/#/gdhydxlogin)，在登陆前进入F12——网络，抓包，获取token和budingID。
2. 可选：如果你希望接收推送通知，可以接入bark，配合服务器自动查询并推送到手机上。(附赠闪电图标)
   
[![V8Nc68.th.png](https://i.imgloc.com/2023/06/20/V8Nc68.th.png)](https://imgloc.com/i/V8Nc68)
4. 运行代码。

## 依赖

- `requests` 库：用于发送 HTTP 请求。
- `json` 库：用于解析 JSON 数据。
- `time` 库：用于添加延迟。

## 配置

在代码中的以下位置填写正确的参数：

```python
# 参数
token = '...'
budingID = '...'
comAddress = '...'
bark_token = '...'
```
## 注意事项
确保你的网络连接正常，以便能够成功发送请求和接收响应。
如果电费查询失败，请检查你的校园网连接。
如果你希望接收推送通知，请确保提供了有效的 Bark token，并且你的设备能够接收到推送通知。

## 其他说明
#### 重新学习了python的函数及其参数的使用方式
#### 保留了playwright的可视化版本

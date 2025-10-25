# 🧠 GDOU 电费查询 + Bark 推送

> 自动登录 → 获取 token → 查宿舍电表 → 刷新抄表 → 查询最新数据 → Bark 推送。  
> 轻量、稳定、无浏览器依赖的广东海洋大学宿舍电费查询脚本。

---

## 🌟 特性

- 一条命令即可获取最新电量、电费余额、更新时间等信息  
- 成功 / 失败 均支持 **Bark** 推送通知  
- 纯 `requests` 实现，无 Selenium / 浏览器依赖  
- 自动抄表刷新，避免读取旧数据  
- 清晰的错误提示与异常捕获

---

## 🧩 原理与流程

1. 登录学生账号（验证学号与密码）  
2. 生成签名并获取 **App Token**  
3. 查询宿舍电表基础信息（楼栋、表号等）  
4. 触发一次抄表刷新  
5. 获取最新电表读数与更新时间  
6. 将结果通过 **Bark 推送** 至手机

---

## 🧰 环境要求

- Python ≥ 3.8  
- 网络可访问学校用电系统接口  

安装依赖：
```bash
pip install requests
````

---

## 🚀 快速开始

### 1. 克隆项目并安装依赖

```bash
git clone https://github.com/louis16s/gdou_electricity.git
cd gdou-electric
pip install -r requirements.txt
```

### 2. 配置学号与密码

打开 `electric_requests.py`，找到：

```python
STUDENT_NAME   = ""  # 姓名，可留空
STUDENT_OUTID  = ""  # 学号/一卡通号
STUDENT_PWD    = ""  # 登录密码
```

### 3. （可选）配置 Bark 推送

* 推荐使用环境变量：

  ```bash
  export BARK_TOKEN="你的Bark令牌"
  ```
* 或直接修改脚本中的：

  ```python
  DEFAULT_BARK_TOKEN = os.getenv("BARK_TOKEN", "")
  ```

### 4. 运行

```bash
python electric_requests.py
```



## 📄 输出示例

终端输出：

```
登录成功，返回数据：{...}
获取到 token: eyJhbGciOi...
电表信息如下：
leftMoney: 23.50
meterData: 1234.56
updateDateTime: 2025-10-18 09:32:10
```

Bark 推送内容：

```
[2025-10-18][09:35:42]
余额: 23.50
总电量(kWh): 1234.56
更新时间: 2025-10-18 09:32:10
```



## ⚙️ 可配置项

| 变量名                  | 说明            | 默认值     |
| -------------------- | ------------- | ------- |
| `STUDENT_NAME`       | 学生姓名          | `""`    |
| `STUDENT_OUTID`      | 学号/一卡通账号      | 必填      |
| `STUDENT_PWD`        | 登录密码          | 必填      |
| `DEFAULT_BARK_TOKEN` | Bark 令牌       | 从环境变量读取 |
| `BARK_ICON`          | Bark 通知图标 URL | 可选      |
| `BASE`               | 电费系统接口地址      | 默认校内    |

---


### Windows

使用“任务计划程序”：

* 时间：每天 07:30、19:30
* 程序：`python.exe`
* 参数：`C:\path\to\electric_requests.py`


## 🔒 安全与隐私

* 默认关闭 HTTPS 证书校验（`verify=False`），仅建议在校园网环境使用

  * 若需启用校验，请修改为 `verify=True` 或提供 CA 证书路径
* 避免上传包含学号、密码、Bark 令牌的文件到 GitHub

  * 使用 `.env` 或环境变量管理敏感信息



## 🧠 常见问题 (FAQ)

**Q：登录失败或返回 code != 0？**
A：检查账号密码是否正确，或系统是否更新了登录接口。

**Q：抄表失败？**
A：学校系统可能在维护，或电表接口字段发生变化。

**Q：Bark 没有推送？**
A：确认 `BARK_TOKEN` 是否正确，是否能访问 `https://api.day.app/`。

**Q：为什么要先刷新抄表？**
A：系统查询接口常返回上次采集结果，刷新可确保数据最新。



## 🧑‍💻 二次开发指南

主要函数：

| 函数名                        | 功能说明       |
| -------------------------- | ---------- |
| `login_student()`          | 登录账号       |
| `get_app_token()`          | 获取 token     |
| `get_meter_infoallmatch()` | 查询宿舍电表    |
| `refresh_meter()`          | 触发抄表       |
| `get_meter_status()`       | 查询电表状态    |
| `send_bark()`              | 推送 Bark 通知 |

核心逻辑位于 `main()` 函数，异常会被捕获并通过 Bark 推送。


## ⚠️ 免责声明

本项目仅供学习与个人使用，请遵守学校网络与数据使用规范。
因接口变更、系统维护或网络异常导致的数据误差或不可用，责任由使用者自负。



## 🔭 延伸想法

* 结合 SQLite/CSV 记录每日用电量，绘制趋势曲线
* 设置余额阈值自动推送提醒（低于 5 元时自动响铃）
* 集成钉钉 / 飞书 / Telegram Bot 实现多平台通知


---

```
✨ “能量守恒不止于物理，也体现在每次查询电费的理性之中。”
```


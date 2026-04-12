# 网易企业邮箱配置报告

> **生成时间**: 2026-04-12 21:55
> **配置者**: Iris 🐦‍⬛

---

## 一、邮箱信息

| 项目 | 值 |
|------|-----|
| 邮箱地址 | limin.ren@bangcle.com |
| 邮箱类型 | 网易企业邮箱 |
| IMAP 服务器 | imap.qiye.163.com:993 (SSL) |
| SMTP 服务器 | smtp.qiye.163.com:465 (SSL) |
| 认证方式 | 客户端授权码 |

---

## 二、连接测试结果

| 测试项 | 结果 | 说明 |
|--------|------|------|
| IMAP 接收 | ✅ 成功 | 收件箱 80301 封邮件 |
| SMTP 发送 | ✅ 成功 | 连接正常 |
| SSL 证书 | ⚠️ 需跳过验证 | 企业证书链问题 |

---

## 三、邮箱结构

| 文件夹 | 说明 |
|--------|------|
| INBOX | 收件箱 (80301 封) |
| &g0l6P3ux- | 已发送 |
| &XfJT0ZAB- | 草稿箱 |
| &XfJSIJZk- | 已删除 |
| &V4NXPpCuTvY- | 垃圾邮件 |

---

## 四、配置代码

### IMAP 连接
```python
import imaplib
import ssl

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

imap = imaplib.IMAP4_SSL("imap.qiye.163.com", 993, ssl_context=context)
imap.login("limin.ren@bangcle.com", "<授权码>")
status, messages = imap.select("INBOX")
print(f"收件箱邮件数: {messages[0].decode()}")
```

### SMTP 连接
```python
import smtplib
import ssl

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

smtp = smtplib.SMTP_SSL("smtp.qiye.163.com", 465, context=context)
smtp.login("limin.ren@bangcle.com", "<授权码>")
```

---

## 五、Keychain 存储

| 键名 | 值 |
|------|-----|
| openclaw-browser-iris-email-username | limin.ren@bangcle.com |
| openclaw-browser-iris-email-password | 93DxBqytbdR%242$ |

---

_配置者: Iris 🐦‍⬛_

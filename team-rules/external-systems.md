# 外部系统接入文档 v1.0

> **目的**: 集中管理所有外部系统的接入配置
> **维护者**: Jerry (定期更新)

---

## 一、系统清单

| 系统 | 负责 Agent | 用途 | 接入方式 | 状态 |
|------|-----------|------|---------|------|
| 泛微 OA | Ella 🦊 | 合同审批流程 | API | ⏳ 待配置 |
| 万事 ONES | Oliver 🐘 | 项目管理 | API | ⏳ 待配置 |
| 网易邮箱 | Iris 🐦‍⬛ | 邮件收发 | IMAP/SMTP | ⏳ 待配置 |
| Office 365 | Iris 🐦‍⬛ | 邮件/日历 | OAuth | ⏳ 待配置 |
| 企业微信 | Jerry 🦞 | 消息通道 | WebSocket | ✅ 已接入 |
| ClawChat | Jerry 🦞 | 消息通道 | HTTP Polling | ✅ 已接入 |
| 百炼 API | 全局 | AI 模型 | REST API | ✅ 已接入 |
| GitHub | 全局 | 代码备份 | PAT | ✅ 已接入 |
| Tavily API | 全局 | 搜索服务 | REST API | ✅ 已接入 |

---

## 二、待配置系统

### 2.1 泛微 OA
- **API 地址**: 待提供
- **认证方式**: 待确认
- **负责 Agent**: Ella

### 2.2 万事 ONES
- **API 地址**: 待提供
- **认证方式**: 待确认
- **负责 Agent**: Oliver

### 2.3 网易邮箱
- **IMAP 服务器**: 待确认
- **SMTP 服务器**: 待确认
- **负责 Agent**: Iris

### 2.4 Office 365
- **OAuth 端点**: 待确认
- **Client ID**: 待提供
- **负责 Agent**: Iris

---

## 三、凭证管理

所有外部系统凭证存储在 macOS Keychain 中：

```bash
# 存储凭证
security add-generic-password \
    -s "openclaw-{system}-{credential}" \
    -a "{agent}" \
    -w "{value}" \
    -U
```

---

_创建时间: 2026-04-12 15:03 | 版本: v1.0 | 作者: Jerry 🦞_

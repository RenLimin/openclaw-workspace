# Agent 路由规则 v1.0

> **目的**: 定义消息如何路由到正确的 Agent
> **原则**: 按职责路由，未知消息默认到 Jerry

---

## 一、路由策略

### 1.1 默认路由

| Channel | 默认 Agent | 说明 |
|---------|-----------|------|
| 企业微信 (wecom) | Jerry 🦞 | 所有消息先到 Jerry，由 Jerry 分发 |
| 微信小程序 (openclawwechat) | Jerry 🦞 | 所有消息先到 Jerry |
| WebChat | Jerry 🦞 | Rex 直接对话 |

### 1.2 关键词路由

| 关键词 | 路由到 | 说明 |
|--------|--------|------|
| 合同、审批、OA、法务 | Ella 🦊 | 合同相关 |
| 项目、ONES、进度、里程碑 | Oliver 🐘 | 项目相关 |
| 经营、报表、预算、KPI | Aaron 🦉 | 经营相关 |
| 邮件、通知、日程、文档 | Iris 🐦‍⬛ | 辅助相关 |
| 其他 | Jerry 🦞 | 默认协调 |

### 1.3 命令路由

| 命令 | 路由到 | 说明 |
|------|--------|------|
| `/ella` | Ella 🦊 | 直接对话 Ella |
| `/oliver` | Oliver 🐘 | 直接对话 Oliver |
| `/aaron` | Aaron 🦉 | 直接对话 Aaron |
| `/iris` | Iris 🐦‍⬛ | 直接对话 Iris |

---

## 二、Jerry 分发机制

```
用户消息 → Jerry 分析意图
   │
   ├── 合同/OA → 转发 Ella
   ├── 项目/ONES → 转发 Oliver
   ├── 经营/报表 → 转发 Aaron
   ├── 邮件/辅助 → 转发 Iris
   └── 其他/协调 → Jerry 处理
```

---

## 三、配置命令

```bash
# 绑定企业微信到 Jerry
openclaw agents bind --agent jerry --bind wecom:default

# 绑定微信小程序到 Jerry
openclaw agents bind --agent jerry --bind openclawwechat:default

# 查看所有路由
openclaw agents bindings
```

---

_创建时间: 2026-04-12 15:03 | 版本: v1.0 | 作者: Jerry 🦞_

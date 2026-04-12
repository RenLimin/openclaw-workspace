# Agent 监控规则 v1.0

> **目的**: 确保所有 Agent 健康运行，及时发现问题
> **执行者**: Jerry (主代理) 通过 Heartbeat 巡检

---

## 一、监控指标

| 指标 | 检查方式 | 频率 | 异常阈值 |
|------|---------|------|---------|
| Agent 注册状态 | `openclaw agents list` | 每日 | Agent 不在列表中 |
| 工作区完整性 | 检查核心文件 | 每周 | 文件缺失 |
| 技能依赖 | `openclaw skills check` | 每周 | 依赖缺失 |
| 磁盘使用 | `du -sh ~/.openclaw/agents/{name}/` | 每周 | > 500MB |
| 日志更新 | 检查 `memory/YYYY-MM-DD.md` | 每日 | 超过 2 天无更新 |
| Channel 状态 | `openclaw channels status` | 每日 | Channel 断开 |
| Gateway 状态 | `openclaw gateway status` | 每日 | 运行异常 |

---

## 二、告警规则

| 级别 | 条件 | 通知方式 | 响应时间 |
|------|------|---------|---------|
| P0 | Agent 崩溃/Channel 断开 | 立即通知 Rex | 即时 |
| P1 | 技能依赖缺失/磁盘 > 80% | 2h 内通知 Rex | 2h |
| P2 | 日志未更新/性能下降 | 每日汇总通知 | 24h |

---

## 三、故障恢复流程

```
发现故障
   │
   ▼
1. 记录故障信息 (memory/YYYY-MM-DD.md)
   │
   ▼
2. 尝试自动恢复 (最多 3 次)
   │
   ├── 成功 → 记录恢复信息
   │
   ▼ 失败
3. 通知 Rex (P0 立即，P1/P2 延迟)
   │
   ▼
4. 等待 Rex 指令
```

---

_创建时间: 2026-04-12 15:03 | 版本: v1.0 | 作者: Jerry 🦞_

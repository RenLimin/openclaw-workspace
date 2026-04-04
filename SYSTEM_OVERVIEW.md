# 🦞 OpenClaw 系统全景图 v2.0

**生成时间**: 2026-04-04 16:42  
**系统版本**: v2.0.0-20260404  
**GitHub**: https://github.com/RenLimin/openclaw-workspace

---

## 📋 目录

1. [智能体团队](#1-智能体团队)
2. [智能体专属技能](#2-智能体专属技能)
3. [全局共享技能](#3-全局共享技能)
4. [配置文件](#4-配置文件)
5. [脚本工具](#5-脚本工具)
6. [数据库](#6-数据库)
7. [Cron 任务](#7-cron-任务)
8. [文档文件](#8-文档文件)
9. [日志文件](#9-日志文件)

---

## 1. 智能体团队 (6个)

| 智能体 | 职责 | Emoji | 状态 |
|--------|------|-------|------|
| **Jerry** | 主代理 & 团队协调员 | 🦞 | ✅ 运行中 |
| **Ella** | 合同审批和管理 | 🦊 | ✅ 运行中 |
| **Aaron** | 经营报告分析 | 🦉 | ✅ 运行中 |
| **Oliver** | 项目管理 (ONES) | 🐘 | ✅ 运行中 |
| **Iris** | 邮件管理 | 🐦‍⬛ | ✅ 运行中 |
| **Oscar** | OA 流程 | 🐳 | ✅ 运行中 |

### 智能体工作区结构

```
~/.openclaw/workspace/
├── skills/
│   ├── aaron/          # Aaron 专属技能
│   ├── ella/           # Ella 专属技能
│   ├── iris/           # Iris 专属技能
│   ├── jerry/          # Jerry 专属技能
│   ├── oliver/         # Oliver 专属技能
│   └── oscar/          # Oscar 专属技能
└── experiences/
    ├── aaron-rules.json    # Aaron 规则
    ├── ella-rules.json     # Ella 规则
    ├── iris-rules.json     # Iris 规则
    ├── jerry-rules.json    # Jerry 规则 (通用规则源)
    ├── oliver-rules.json   # Oliver 规则
    └── oscar-rules.json    # Oscar 规则
```

---

## 2. 智能体专属技能

### 🦞 Jerry (主代理)
- **技能**: `release-manager` - Release Management 框架
- **脚本**: 
  - `github-auto-commit.sh` - GitHub 自动提交
  - `weekly-github-backup.sh` - 每周全量备份
  - `skill-auto-commit.sh` - 技能自动提交
  - `weekly-full-backup.sh` - 每周全量备份

### 🦊 Ella (合同审批)
- **技能**: `contract-management` - 合同管理
- **数据库**: `contract-management.sqlite`
- **Chrome 数据**: `~/.openclaw/browser/ella/`

### 🦉 Aaron (经营报告)
- **技能**: `report-analyzer` - 报告分析
- **数据库**: `report-analyzer.sqlite`
- **备份**: `202602_delivery_report_v1.9.db`

### 🐘 Oliver (项目管理)
- **技能**: `ones-api` - ONES API 集成
- **数据库**: `ones-project.sqlite`
- **Chrome 数据**: `~/.openclaw/browser/oliver/`

### 🐦‍⬛ Iris (邮件管理)
- **技能**: `iris-email` - 邮件管理
- **数据库**: `email.sqlite`

### 🐳 Oscar (OA 流程)
- **技能**: `oscar-oa` - OA 流程自动化
- **数据库**: `oa-agent.sqlite`
- **Chrome 数据**: `~/.openclaw/browser/oscar/`

---

## 3. 全局共享技能 (42个)

### 核心技能
| 技能名 | 用途 | 版本 |
|--------|------|------|
| agent-browser | 浏览器自动化 | v1.0.0 |
| agent-creator | 智能体创建 | v1.0.0 |
| agent-team-orchestration | 团队编排 | v1.0.0 |
| automate-excel | Excel 自动化 | v1.0.0 |
| automation-workflows | 工作流自动化 | v1.0.0 |
| clawsec | 安全审计 | v1.0.0 |
| cli-anything | CLI 生成 | v1.0.0 |
| conversation-summary | 会话摘要 | v1.0.0 |
| document-recognition | 文档识别 | v1.0.0 |
| excel-weekly-dashboard | Excel 仪表盘 | v1.0.0 |
| feishu-doc | 飞书文档 | v1.0.0 |
| find-skills | 技能发现 | v1.0.0 |
| github | GitHub 集成 | v1.0.0 |
| iris-email | 邮件管理 | v1.0.0 |
| memos-memory-guide | 记忆管理 | v1.0.0 |
| mission-control | 任务控制 | v1.0.0 |
| office-excel | Excel 操作 | v1.0.0 |
| office-ppt | PPT 操作 | v1.0.0 |
| office-report | 报告生成 | v1.0.0 |
| office-word | Word 操作 | v1.0.0 |
| ones-api | ONES API | v1.0.0 |
| ontology | 知识图谱 | v1.0.0 |
| proactive-agent | 主动代理 | v1.0.0 |
| self-improving-agent | 自我进化 | v1.0.0 |
| skill-creator | 技能创建 | v1.0.0 |
| skill-trainer | 技能训练 | v1.0.0 |
| skill-vetter | 技能审核 | v1.0.0 |
| summarize | 文本摘要 | v1.0.0 |
| system-monitor | 系统监控 | v1.0.0 |
| tavily-search | Tavily 搜索 | v1.0.0 |
| web | Web 开发 | v1.0.0 |
| web-perf | Web 性能 | v1.0.0 |

---

## 4. 配置文件

### 核心配置
| 文件 | 用途 | 敏感信息 |
|------|------|----------|
| `~/.openclaw/openclaw.json` | Gateway 主配置 | ✅ 有 (Token) |
| `~/.openclaw/workspace/AGENTS.md` | 智能体规范 | ❌ 无 |
| `~/.openclaw/workspace/HEARTBEAT.md` | 心跳检查清单 | ❌ 无 |
| `~/.openclaw/workspace/IDENTITY.md` | Jerry 身份信息 | ❌ 无 |
| `~/.openclaw/workspace/SOUL.md` | 智能体灵魂 | ❌ 无 |
| `~/.openclaw/workspace/TOOLS.md` | 工具配置 | ✅ 有 (凭证) |
| `~/.openclaw/workspace/USER.md` | 用户信息 | ❌ 无 |

### Git 配置
| 文件 | 用途 |
|------|------|
| `.gitignore` | Git 忽略规则 |
| `.git/config` | Git 配置 |
| `.git/config` 代理 | http.proxy: http://127.0.0.1:7897 |

---

## 5. 脚本工具

### 自动化脚本 (位于 `~/.openclaw/workspace/scripts/`)
| 脚本 | 用途 | 频率 |
|------|------|------|
| `github-auto-commit.sh` | GitHub 自动提交 | 每 6 小时 |
| `weekly-github-backup.sh` | 每周全量备份 | 每周日 02:00 |
| `skill-auto-commit.sh` | 技能自动提交 | 手动 |
| `weekly-full-backup.sh` | 全量备份 | 每周日 02:00 |

---

## 6. 数据库

### SQLite 数据库文件
| 数据库 | 用途 | 大小 | 敏感数据 |
|--------|------|------|----------|
| `~/.openclaw/tasks/runs.sqlite` | 任务执行记录 | ~MB | ❌ 无 |
| `~/.openclaw/memory/email.sqlite` | 邮件记忆 | ~MB | ✅ 有 |
| `~/.openclaw/memory/contract-management.sqlite` | 合同数据 | ~MB | ✅ 有 |
| `~/.openclaw/memory/report-analyzer.sqlite` | 报告数据 | ~MB | ✅ 有 |
| `~/.openclaw/memory/ones-project.sqlite` | ONES 数据 | ~MB | ✅ 有 |
| `~/.openclaw/memory/main.sqlite` | 主记忆 | ~MB | ✅ 有 |
| `~/.openclaw/memory/oa-agent.sqlite` | OA 数据 | ~MB | ✅ 有 |

### Chrome 数据文件
| 路径 | 用途 |
|------|------|
| `~/.openclaw/browser/ella/` | Ella Chrome 数据 |
| `~/.openclaw/browser/oliver/` | Oliver Chrome 数据 |
| `~/.openclaw/browser/oscar/` | Oscar Chrome 数据 |

---

## 7. Cron 任务 (16个)

### 系统监控任务
| 任务 | 频率 | 状态 |
|------|------|------|
| 心跳检查 (P0) | 每小时 | ✅ ok |
| 训练决策通知监控 (P1) | 每小时 | ✅ ok |
| 进度汇报 (工作时间 P1) | 每 2 小时 | ✅ ok |
| 进度汇报 (非工作时间 P2) | 每 4 小时 | ✅ ok |

### GitHub 相关任务
| 任务 | 频率 | 状态 |
|------|------|------|
| GitHub 技能自动提交检查 | 每 6 小时 | ⏳ idle |
| GitHub 远程备份 (P2) | 每周六22:00 | ✅ ok |
| GitHub 每周全量备份 | 每周日02:00 | ⏳ idle |

### 备份任务
| 任务 | 频率 | 状态 |
|------|------|------|
| 本地系统备份 (P2) | 每天 23:00 | ✅ ok |
| OpenClaw 全量备份 | 每周日 02:00 | ⏳ idle |
| 临时文件清理 (P2) | 每周六 09:30 | ✅ ok |
| 记忆归档 (P2) | 每周六 09:00 | ✅ ok |

### 维护任务
| 任务 | 频率 | 状态 |
|------|------|------|
| Gateway 定期重启 | 每周六 23:45 | ⏳ idle |
| 智能体团队健康检查 | 每周日 10:00 | ⏳ idle |
| 团队周回顾 | 每周日 17:00 | ✅ ok |
| 训练周总结 | 每周五 17:00 | ✅ ok |

---


## 8. 文档文件

### 核心文档
| 文件 | 用途 | 大小 |
|--------|------|--------|
| `README.md` | 仓库说明 | ~1KB |
| `AGENTS.md` | 智能体规范 | ~10KB |
| `HEARTBEAT.md` | 心跳检查 | ~5KB |
| `IDENTITY.md` | Jerry 身份 | ~2KB |
| `SOUL.md` | 智能体灵魂 | ~3KB |
| `TOOLS.md` | 工具配置 | ~5KB |
| `USER.md` | 用户信息 | ~3KB |
| `SYSTEM_OVERVIEW.md` | 系统全景图 | ~15KB |

### 技能文档
每个技能包含:
- `SKILL.md` - 技能说明
- `VERSION` - 版本号
- `CHANGELOG.md` - 变更日志 (可选)
- `README.md` - 技能说明 (可选)

---

## 9. 日志文件

### 日志目录: `~/.openclaw/logs/`

| 日志文件 | 大小 | 说明 |
|----------|------|------|
| `gateway.log` | ~40MB | Gateway 主日志 |
| `gateway.err.log` | ~57MB | Gateway 错误日志 |
| `wake-recovery-*.log` | <1KB | 唤醒恢复日志 |
| `network-keepalive.log` | ~100KB | 网络保活日志 |

---

## 📊 系统统计

| 项目 | 数量 |
|------|------|
| 智能体 | 6 个 |
| 专属技能 | 6 个 |
| 全局技能 | 42 个 |
| 脚本 | 4 个 |
| 数据库 | 7 个 |
| Cron 任务 | 16 个 |
| 配置文件 | 8 个 |

---

## 🔗 外部集成

| 服务 | 状态 | 配置位置 |
|------|------|----------|
| GitHub | ✅ 已连接 | `openclaw.json` |
| 企业微信 | ✅ 已配置 | `openclaw.json` |
| ClawChat | ✅ 已配置 | `openclaw.json` |
| ONES | ✅ 已配置 | `TOOLS.md` |
| 网易邮箱 | ✅ 已配置 | `TOOLS.md` |
| 泛微 OA | ✅ 已配置 | `TOOLS.md` |

---

## 🎯 系统状态

| 指标 | 状态 | 说明 |
|------|------|------|
| Gateway | ✅ live | PID 877 |
| Cron 健康 | ✅ 15/15 | 无错误 |
| 磁盘使用 | ⚠️ 93% | 33Gi 可用 |
| 内存使用 | ✅ 正常 | 11% 可用 |
| GitHub 同步 | ✅ 已推送 | 最新提交 |

---

*最后更新: 2026-04-04 16:42*

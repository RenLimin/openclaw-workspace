# 📋 OpenClaw 系统详细清单

**生成时间**: 2026-04-04 16:52  
**系统版本**: v2.0.0-20260404

---

## 1. 智能体团队详细配置 (6个)

### 🦞 Jerry (主代理)
**工作区**: `~/.openclaw/workspace/skills/jerry/`
- 目录: (空，使用全局技能)

**专属技能**:
- `release-manager` - Release Management 框架

**数据库**:
- `~/.openclaw/memory/main.sqlite` (68K)

---

### 🦊 Ella (合同审批)
**工作区**: `~/.openclaw/workspace/skills/ella/`
- CHANGELOG.md
- README.md
- SKILL.md
- VERSION
- versions/

**专属技能**:
- `contract-management` - 合同管理

**数据库**:
- `~/.openclaw/memory/contract-management.sqlite` (68K)

**Chrome 数据**:
- `~/.openclaw/browser/ella/`

---

### 🦉 Aaron (经营报告)
**工作区**: `~/.openclaw/workspace/skills/aaron/`
- CHANGELOG.md
- README.md
- SKILL.md
- VERSION
- scripts/

**专属技能**:
- `report-analyzer` - 报告分析

**数据库**:
- `~/.openclaw/memory/report-analyzer.sqlite` (68K)

---

### 🐘 Oliver (项目管理)
**工作区**: `~/.openclaw/workspace/skills/oliver/`
- ones-project-management/

**专属技能**:
- `ones-api` - ONES API 集成

**数据库**:
- `~/.openclaw/memory/ones-project.sqlite` (68K)

**Chrome 数据**:
- `~/.openclaw/browser/oliver/`

---

### 🐦‍⬛ Iris (邮件管理)
**工作区**: `~/.openclaw/workspace/skills/iris/`
- email-management/

**专属技能**:
- `iris-email` - 邮件管理

**数据库**:
- `~/.openclaw/memory/email.sqlite` (68K)

---

### 🐳 Oscar (OA 流程)
**工作区**: `~/.openclaw/workspace/skills/oscar/`
- oa-automation/

**专属技能**:
- `oscar-oa` - OA 流程自动化

**数据库**:
- `~/.openclaw/memory/oa-agent.sqlite` (68K)

**Chrome 数据**:
- `~/.openclaw/browser/oscar/`

---

## 2. 全局共享技能 (42个)

| 技能名 | 结构 |
|--------|------|
| agent-browser | versions/ |
| agent-creator | references/, templates/, versions/ |
| agent-team-orchestration | versions/ |
| automate-excel | versions/ |
| automation-workflows | versions/ |
| clawsec | versions/ |
| cli-anything | versions/ |
| conversation-summary | versions/ |
| document-recognition | versions/ |
| excel-weekly-dashboard | versions/ |
| feishu-doc | versions/ |
| find-skills | versions/ |
| github | versions/ |
| iris-email | versions/ |
| memos-memory-guide | SKILL.md, versions/ |
| mission-control | CHANGELOG.md, LICENSE, README.md |
| obsidian-cli-official | versions/ |
| office-excel | versions/ |
| office-ppt | versions/ |
| office-report | versions/ |
| office-word | versions/ |
| ones-api | versions/ |
| ontology | versions/ |
| oscar-oa | scripts/, versions/ |
| proactive-agent | versions/ |
| product-catalog | versions/ |
| project-doc-GJSWZJ | CHANGELOG.md, DOCUMENTS.md, HANDOVER.md |
| release-manager | SKILL.md, VERSION, __init__.py |
| self-improving-agent | versions/ |
| skill-creator | versions/ |
| skill-trainer | assets/, examples/, versions/ |
| skill-vetter | versions/ |
| summarize | versions/ |
| system-monitor | references/, versions/ |
| tavily-search | versions/ |
| web | versions/ |
| web-perf | versions/ |

---

## 3. 配置文件清单 (9个)

| 文件 | 大小 | 用途 |
|------|------|------|
| `~/.openclaw/openclaw.json` | 18K | Gateway 主配置 |
| `~/.openclaw/workspace/AGENTS.md` | 7.7K | 智能体规范 |
| `~/.openclaw/workspace/HEARTBEAT.md` | 193B | 心跳检查清单 |
| `~/.openclaw/workspace/IDENTITY.md` | 636B | Jerry 身份信息 |
| `~/.openclaw/workspace/README.md` | 92B | 仓库说明 |
| `~/.openclaw/workspace/SOUL.md` | 1.6K | 智能体灵魂 |
| `~/.openclaw/workspace/SYSTEM_OVERVIEW.md` | 9.1K | 系统全景图 |
| `~/.openclaw/workspace/TOOLS.md` | 860B | 工具配置 |
| `~/.openclaw/workspace/USER.md` | 477B | 用户信息 |

---

## 4. 数据库清单 (7个)

| 数据库 | 大小 | 用途 | 敏感数据 |
|--------|------|------|----------|
| `~/.openclaw/memory/contract-management.sqlite` | 68K | 合同数据 | ✅ 有 |
| `~/.openclaw/memory/email.sqlite` | 68K | 邮件数据 | ✅ 有 |
| `~/.openclaw/memory/main.sqlite` | 68K | 主记忆 | ✅ 有 |
| `~/.openclaw/memory/oa-agent.sqlite` | 68K | OA 数据 | ✅ 有 |
| `~/.openclaw/memory/ones-project.sqlite` | 68K | ONES 数据 | ✅ 有 |
| `~/.openclaw/memory/report-analyzer.sqlite` | 68K | 报告数据 | ✅ 有 |
| `~/.openclaw/tasks/runs.sqlite` | 608K | 任务执行记录 | ❌ 无 |

---

## 5. Cron 任务清单 (15个)

### 系统监控 (4个)
| ID | 名称 | 频率 | 状态 |
|----|------|------|------|
| 8629fc38-d02c-48a0-8673-2cca90a6bae2 | 心跳检查 (P0) | 每小时 | ✅ ok |
| 17121501-ec39-4994-86ac-bb96000a269c | 训练决策通知监控 (P1) | 每小时 | ✅ ok |
| 636faa57-c630-4366-8129-a5df90f5d4d0 | 进度汇报 (工作时间 P1) | 每 2 小时 | ✅ ok |
| e42b19be-35c5-4264-b3cd-191d662bb749 | 进度汇报 (非工作时间 P2) | 每 4 小时 | ✅ ok |

### GitHub 相关 (3个)
| ID | 名称 | 频率 | 状态 |
|----|------|------|------|
| 92502676-3d08-4a17-9d84-9547ca2a6412 | GitHub 技能自动提交检查 | 每 6 小时 | ⏳ idle |
| 3509d6b8-7b6a-4b71-b554-43292551b4bf | GitHub 远程备份 (P2) | 每周六 22:00 | ✅ ok |
| f8ce8212-43c0-4e96-bccb-106c71cece0b | GitHub 每周全量备份 | 每周日 02:00 | ⏳ idle |

### 备份任务 (4个)
| ID | 名称 | 频率 | 状态 |
|----|------|------|------|
| c6517cac-b555-4674-a4ad-774156862b9a | 本地系统备份 (P2) | 每天 23:00 | ✅ ok |
| 532089dc-9c17-4eea-b6cb-410729111f16 | OpenClaw 全量备份 | 每周日 02:00 | ⏳ idle |
| fc761409-f402-412b-bed8-cc9c7dea316b | 记忆归档 (P2) | 每周六 09:00 | ✅ ok |
| 5a1563e4-6034-46a1-9d14-0b77b9abcb35 | 临时文件清理 (P2) | 每周六 09:30 | ✅ ok |

### 维护任务 (4个)
| ID | 名称 | 频率 | 状态 |
|----|------|------|------|
| 4e08a66a-1ca6-46a3-bf29-8beb41a12d39 | Gateway 定期重启 | 每周六 23:45 | ⏳ idle |
| 73d0bf79-7a04-4ab1-85fd-2275ef8612b7 | 智能体团队健康检查 | 每周日 10:00 | ⏳ idle |
| 1ccef0bb-3e88-418d-962b-48587693b490 | 团队周回顾 | 每周日 17:00 | ✅ ok |
| 015452e1-2ddf-4d35-bbb3-f72189853e8a | 训练周总结 | 每周五 17:00 | ✅ ok |

---

## 6. 脚本目录

**路径**: `~/.openclaw/workspace/scripts/`

当前为空 (脚本已清理或移至其他位置)

---

## 7. 经验文件

**路径**: `~/.openclaw/experiences/`

当前为空或未找到

---

## 📊 系统统计

| 项目 | 数量 |
|------|------|
| 智能体 | 6 个 |
| 专属技能 | 6 个 |
| 全局技能 | 42 个 |
| 配置文件 | 9 个 |
| 数据库 | 7 个 |
| Cron 任务 | 15 个 |

---

*最后更新: 2026-04-04 16:52*

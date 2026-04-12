# OpenClaw 智能体团队系统全貌 v3.0

> **更新时间**: 2026-04-12 15:30
> **系统版本**: OpenClaw 2026.4.10
> **模型**: bailian/qwen3.6-plus

---

## 一、系统架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                        OpenClaw Gateway                         │
│                   (ws://127.0.0.1:18789)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
        ┌─────▼─────┐ ┌────▼─────┐ ┌─────▼─────┐
        │ 企业微信   │ │ ClawChat │ │  WebChat  │
        │  (wecom)  │ │(miniprog)│ │  (Web)    │
        └─────┬─────┘ └────┬─────┘ └─────┬─────┘
              │             │             │
              └─────────────┼─────────────┘
                            │
                    ┌───────▼───────┐
                    │  Jerry 🦞    │
                    │ (主代理)      │
                    └───┬───┬───┬───┘
                        │   │   │   │
              ┌─────────┘   │   │   └─────────┐
              │             │   │             │
        ┌─────▼─────┐ ┌────▼─────┐ ┌────────▼────────┐ ┌────▼────┐
        │ Ella 🦊   │ │Oliver 🐘 │ │ Aaron 🦉       │ │ Iris 🐦‍⬛│
        │ 合同管理  │ │项目管理  │ │ 经营计划       │ │ 辅助工作│
        └───────────┘ └──────────┘ └────────────────┘ └─────────┘
```

---

## 二、Agent 团队 (5 个)

| Agent | Emoji | 角色 | 状态 | 目录 | 模型 |
|-------|-------|------|------|------|------|
| **Jerry** | 🦞 | 主代理 & 团队协调员 | ✅ active | `~/.openclaw/agents/main/` | bailian/qwen3.6-plus |
| **Ella** | 🦊 | 合同管理 (含 OA 审批) | ✅ active | `~/.openclaw/agents/ella/` | bailian/qwen3.6-plus |
| **Oliver** | 🐘 | 项目管理 (含 ONES 操作) | ✅ active | `~/.openclaw/agents/oliver/` | bailian/qwen3.6-plus |
| **Aaron** | 🦉 | 经营计划 | ✅ active | `~/.openclaw/agents/aaron/` | bailian/qwen3.6-plus |
| **Iris** | 🐦‍⬛ | 辅助工作 (含 邮件管理) | ✅ active | `~/.openclaw/agents/iris/` | bailian/qwen3.6-plus |

### Agent 注册表

```json
{
  "version": "2.0",
  "updatedAt": "2026-04-12T14:37:00+08:00",
  "agents": { "jerry": {...}, "ella": {...}, "oliver": {...}, "aaron": {...}, "iris": {...} }
}
```

---

## 三、消息通道 (3 个)

| Channel | 类型 | 状态 | 配置 | 负责 Agent |
|---------|------|------|------|-----------|
| **企业微信** | WebSocket | ✅ running | Bot ID + Secret | Jerry 🦞 |
| **ClawChat** | HTTP Polling | ⚠️ 未配置 | API Key | Jerry 🦞 |
| **WebChat** | WebSocket | ✅ running | Loopback | Jerry 🦞 |

### 插件配置

| 插件 | 版本 | 状态 | 说明 |
|------|------|------|------|
| wecom-openclaw-plugin | 2026.4.8 | ✅ enabled | 企业微信通道 |
| openclawwechat | 1.3.2 | ✅ enabled | 微信小程序通道 |

---

## 四、技能体系

### 4.1 技能统计

| 指标 | 数量 |
|------|------|
| **总技能数** | 88 |
| **可用技能** | 45 |
| **缺失依赖** | 43 |

### 4.2 L0-L3 全局共享技能 (24 个)

| 层级 | 技能 | 版本 | 用途 |
|------|------|------|------|
| **L0 核心** | self-improving | 1.2.16 | 自我进化 |
| | proactive-agent-lite | 1.0.0 | 主动触发 |
| | openclaw-memory | 1.0.0 | 记忆管理 |
| | context-scope-tags | 0.2.0 | 上下文增强 |
| | prompt-enhancer | 1.0.1 | 提示词优化 |
| **L1 安全** | openclaw-skill-vetter | 1.0.0 | 技能审核 |
| | code-interpreter | 1.0.0 | 代码执行 |
| **L2 信息** | openclaw-tavily-search | 0.1.0 | Tavily 搜索 |
| | websearch-free-skill | 0.1.1 | 网页搜索 |
| | summarize-pro | 1.0.0 | 总结提炼 |
| | ontology | 1.0.4 | 知识图谱 |
| | doc-learning | 1.0.0 | 文档学习 |
| | brainstorming-tazio | 1.0.0 | 头脑风暴 |
| **L3 质量** | runesleo-systematic-debugging | 3.0.0 | 调试 |
| | feedback-loop | 1.0.0 | 反馈收集 |
| | test-driven-development | 1.0.0 | 测试驱动 |
| **浏览器** | playwright-browser-automation | 2.0.0 | 浏览器自动化 |
| **PDF/OCR** | pdf-ocr-extraction | 1.0.3 | PDF OCR |
| **Excel** | excel-xlsx | 1.0.2 | Excel 解析 |
| | excel-formula | 2.0.1 | Excel 公式 |
| | generate-excel | 1.0.0 | Excel 生成 |
| **Word** | word-docx | 1.0.2 | Word 解析 |
| | generate-word-docx | 1.0.0 | Word 生成 |
| **PPT** | pptx-generator | 1.0.2 | PPT 生成 |

### 4.3 L4 Agent 专属技能 (5 个)

| Agent | 技能 | 用途 |
|-------|------|------|
| **Ella 🦊** | oa-approval | OA 审批 |
| | contract-management | 合同管理 |
| **Oliver 🐘** | ones-integration | ONES 操作 |
| **Aaron 🦉** | business-analysis | 经营分析 |
| **Iris 🐦‍⬛** | email-management | 邮件管理 |

### 4.4 技能目录结构

```
skills/
├── <skill-name>/
│   ├── SKILL.md           # 技能说明
│   ├── _meta.json         # ClawHub 元数据
│   ├── scripts/           # 自动化脚本
│   ├── references/        # 参考资料
│   └── DEPENDENCIES.md    # 依赖文档
└── ...
```

---

## 五、规则体系 (16 个文件)

### 5.1 团队规则

| 文件 | 大小 | 用途 |
|------|------|------|
| `general-rules.md` | 4.3KB | 通用行为准则 |
| `security-rules.md` | 2.1KB | 安全规范 |
| `training-rules.md` | 3.8KB | 训练规范 |
| `github-rules.md` | 5.3KB | Git 操作规范 |
| `skill-rules.md` | 7.9KB | 技能管理规则 |
| `network-rules.md` | 3.2KB | 网络代理规则 |
| `environment-config.md` | 3.0KB | 环境配置 |

### 5.2 框架文档

| 文件 | 大小 | 用途 |
|------|------|------|
| `skill-training-framework.md` | 19.4KB | 技能训练框架 |
| `agent-creation-framework.md` | 21.9KB | Agent 创建框架 |

### 5.3 运维规则

| 文件 | 大小 | 用途 |
|------|------|------|
| `agent-routing-rules.md` | 1.8KB | 消息路由规则 |
| `agent-monitoring.md` | 1.5KB | Agent 健康监控 |
| `error-escalation.md` | 2.1KB | 错误升级链路 |
| `agent-communication.md` | 2.2KB | 跨 Agent 通信 |
| `external-systems.md` | 1.6KB | 外部系统文档 |
| `knowledge-base.md` | 1.8KB | 知识库结构 |
| `shared-skills.md` | 2.8KB | 共享技能规划 |

### 5.4 模板文件

```
templates/
├── agent/
│   ├── config.json
│   ├── SOUL.md
│   ├── USER.md
│   ├── AGENTS.md
│   ├── TOOLS.md
│   └── MEMORY.md
└── DEPENDENCIES-template.md
```

---

## 六、核心能力 (7 项)

| 能力 | 状态 | 通过率 | 测试脚本 |
|------|------|--------|---------|
| **1. 浏览器自动化** | ✅ 完成 | 3/3 | capability-1-browser.py |
| **2. PDF/图片解析** | ✅ 完成 | 4/4 | capability-2-ocr.py |
| **3. Excel 解析** | ✅ 完成 | 5/5 | capability-3-excel.py |
| **4. Word 解析** | ✅ 完成 | 4/4 | capability-4-word.py |
| **5. Office 制作** | ✅ 完成 | 3/3 | capability-5-office-gen.py |
| **6. 格式转换** | ✅ 完成 | 5/5 | capability-6-libreoffice.py |
| **7. 动态页面引擎** | ✅ 完成 | 5/5 | dynamic-browser-engine.py |

**总计**: 29/29 (100% 通过)

---

## 七、Python 依赖环境

| 包 | 版本 | 用途 |
|----|------|------|
| python3 | 3.10.6 | 运行时 |
| pandas | 2.3.3 | 数据分析 |
| numpy | 2.2.6 | 数值计算 |
| matplotlib | 3.10.8 | 数据可视化 |
| openpyxl | 3.1.2 | Excel 读写 |
| xlsxwriter | 3.2.9 | Excel 生成 |
| python-pptx | 1.0.2 | PPT 生成 |
| PyMuPDF (fitz) | 1.27.2 | PDF 提取 |
| pytesseract | 0.3.13 | OCR 识别 |
| pdf2image | 最新 | PDF 转图片 |
| playwright | 1.58.0 | 浏览器自动化 |
| formulas | 1.3.4 | Excel 公式执行 |
| requests | 2.32.5 | HTTP 请求 |

---

## 八、外部系统

| 系统 | 负责 Agent | 状态 | 说明 |
|------|-----------|------|------|
| **泛微 OA** | Ella 🦊 | ⏳ 待配置 | API 地址待提供 |
| **万事 ONES** | Oliver 🐘 | ⏳ 待配置 | API 地址待提供 |
| **网易邮箱** | Iris 🐦‍⬛ | ⏳ 待配置 | IMAP/SMTP 待配置 |
| **Office 365** | Iris 🐦‍⬛ | ⏳ 待配置 | OAuth 待配置 |
| **百炼 API** | 全局 | ✅ 已接入 | bailian/qwen3.6-plus |
| **GitHub** | 全局 | ✅ 已接入 | RenLimin/openclaw-workspace |
| **Tavily API** | 全局 | ✅ 已接入 | tvly-dev-1Mhr7o... |

---

## 九、浏览器环境 (5 个独立环境)

| Agent | 目录 | 状态 |
|-------|------|------|
| Jerry 🦞 | `~/.openclaw/browser-data/jerry/` | ✅ |
| Ella 🦊 | `~/.openclaw/browser-data/ella/` | ✅ |
| Oliver 🐘 | `~/.openclaw/browser-data/oliver/` | ✅ |
| Aaron 🦉 | `~/.openclaw/browser-data/aaron/` | ✅ |
| Iris 🐦‍⬛ | `~/.openclaw/browser-data/iris/` | ✅ |

---

## 十、记忆系统

| 指标 | 状态 |
|------|------|
| **索引文件** | 2/4 files · 4 chunks |
| **FTS** | ✅ ready |
| **Vector** | ⚠️ 不可用 (无 embedding provider) |
| **存储** | `~/.openclaw/memory/main.sqlite` |

---

## 十一、Git 仓库

| 项目 | 值 |
|------|-----|
| **仓库** | RenLimin/openclaw-workspace |
| **分支** | main |
| **最新提交** | `bc1bda1` - Phase A+B all rules |
| **总提交数** | 20+ |
| **用户邮箱** | limin.ren@outlook.com |
| **代理** | http://127.0.0.1:7897 (备用) |

---

## 十二、系统配置

### 12.1 Gateway

| 配置项 | 值 |
|--------|-----|
| 地址 | ws://127.0.0.1:18789 |
| 绑定 | loopback |
| 认证 | token |
| 状态 | ✅ running |

### 12.2 模型

| 模型 | 上下文窗口 | 最大 Token | 状态 |
|------|-----------|-----------|------|
| qwen3.6-plus | 1,000,000 | 65,536 | ✅ 默认 |
| qwen3.5-plus | 1,000,000 | 65,536 | ✅ 可用 |
| qwen3-max-2026-01-23 | 262,144 | 65,536 | ✅ 可用 |
| qwen3-coder-next | 262,144 | 65,536 | ✅ 可用 |
| qwen3-coder-plus | 1,000,000 | 65,536 | ✅ 可用 |
| MiniMax-M2.5 | 196,608 | 32,768 | ✅ 可用 |
| glm-5 | 202,752 | 16,384 | ✅ 可用 |
| glm-4.7 | 202,752 | 16,384 | ✅ 可用 |
| kimi-k2.5 | 262,144 | 32,768 | ✅ 可用 |

---

## 十三、待办事项

| 任务 | 优先级 | 负责 | 说明 |
|------|--------|------|------|
| 配置路由绑定 | P0 | Jerry | wecom/openclawwechat → Jerry |
| 外部系统接入 | P1 | 各 Agent | OA/ONES/邮箱配置 |
| Phase 2 训练 | P1 | 全部 | 4 Agent 并行训练 |
| 跨 Agent 协作测试 | P2 | Jerry | 端到端流程测试 |
| 知识库初始化 | P2 | 全部 | 术语表/SOP/API 文档 |

---

_更新时间: 2026-04-12 15:30 | 版本: v3.0 | 作者: Jerry 🦞_

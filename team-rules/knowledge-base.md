# 知识库结构 v1.0

> **目的**: 为团队建立统一的知识管理体系
> **位置**: `~/.openclaw/workspace/knowledge-base/`

---

## 一、目录结构

```
knowledge-base/
├── README.md                    # 知识库说明
├── glossary.md                  # 术语表
├── sop/                         # 标准操作流程
│   ├── contract-approval.md     # 合同审批流程
│   ├── project-tracking.md      # 项目跟踪流程
│   ├── email-processing.md      # 邮件处理流程
│   └── report-generation.md     # 报表生成流程
├── api-docs/                    # API 文档
│   ├── oa-api.md                # 泛微 OA API
│   ├── ones-api.md              # 万事 ONES API
│   └── email-api.md             # 邮件 API
├── training/                    # 培训资料
│   ├── agent-onboarding.md      # Agent 入职指南
│   └── skill-tutorials/         # 技能教程
└── lessons-learned/             # 经验教训
    └── YYYY-MM-DD.md            # 按日期记录
```

---

## 二、术语表模板

```markdown
# 术语表

| 术语 | 全称 | 说明 |
|------|------|------|
| OA | Office Automation | 办公自动化系统 (泛微) |
| ONES | 万事 ONES | 项目管理系统 |
| KPI | Key Performance Indicator | 关键绩效指标 |
| SOP | Standard Operating Procedure | 标准操作流程 |
```

---

## 三、SOP 模板

```markdown
# SOP: {流程名称}

## 目的
{描述此流程的目的}

## 负责 Agent
{负责执行此流程的 Agent}

## 流程步骤
1. {步骤 1}
2. {步骤 2}
3. {步骤 3}

## 异常处理
- {异常情况}: {处理方式}
```

---

_创建时间: 2026-04-12 15:03 | 版本: v1.0 | 作者: Jerry 🦞_

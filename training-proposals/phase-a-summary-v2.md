# Phase A 训练方案汇总 (v2)

> **生成时间**: 2026-04-12 20:15
> **基于**: `/Users/bangcle/Downloads/openclaw-skill/训练计划-20260412.md`
> **生成者**: Jerry 🦞 (汇总)

---

## 一、方案概览

| Agent | 核心目标 | 步骤数 | 待确认项 | 验收标准数 |
|-------|---------|--------|---------|-----------|
| **Ella 🦊** | 合同管理 + OA 浏览器自动化 | 15 步 | 3 项 | 7 项 |
| **Oliver 🐘** | 项目管理 + ONES 浏览器+GraphQL | 12 步 | 3 项 | 7 项 |
| **Aaron 🦉** | 经营管理 + 报告解析 | 14 步 | 1 项 | 8 项 |
| **Iris 🐦‍⬛** | 邮件管理 + Agent Loop | 13 步 | 2 项 | 10 项 |

---

## 二、关键变更 (基于 Rex 反馈)

| 原方案 | 新方案 | 原因 |
|--------|--------|------|
| OA API 调用 | 纯浏览器自动化 | 普通账号无 API 权限 |
| ONES API 调用 | 浏览器为主 + GraphQL 辅助 | API 有数量限制 |
| 经营数据源待提供 | 直接解析真实文件 | 训练计划已提供 |
| 邮箱授权码待提供 | 从 GitHub 备份查询 | 已有备份文件 |

---

## 三、共性问题 (需要 Rex 提供)

| 问题 | 涉及 Agent | 说明 |
|------|-----------|------|
| 泛微 OA URL | Ella | OA 系统登录地址 |
| ONES URL | Oliver | ONES 系统登录地址 |
| Word 模板路径 | Aaron | `project delivery/` 目录不存在 |
| GitHub 备份位置 | Iris | 授权码所在仓库和文件 |

---

## 四、方案文件

- [`ella-phase-a-v2.md`](file:///Users/bangcle/.openclaw/workspace/training-proposals/ella-phase-a-v2.md)
- [`oliver-phase-a-v2.md`](file:///Users/bangcle/.openclaw/workspace/training-proposals/oliver-phase-a-v2.md)
- [`aaron-phase-a-v2.md`](file:///Users/bangcle/.openclaw/workspace/training-proposals/aaron-phase-a-v2.md)
- [`iris-phase-a-v2.md`](file:///Users/bangcle/.openclaw/workspace/training-proposals/iris-phase-a-v2.md)

---

## 五、批准后执行

**批准后，我将：**
1. 各 Agent 自主执行 Phase B (预计 4-5h，并行)
2. 遇瓶颈自动转交 Iris 研究
3. 完成后汇总报告给你

---

_汇总者: Jerry 🦞_

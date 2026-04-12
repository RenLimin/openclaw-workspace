# 共享技能规划 v1.0

> **目的**: 定义团队共享技能的需求和管理规范
> **位置**: `~/.openclaw/workspace/skills/`

---

## 一、已安装共享技能 (24 个)

| 技能 | 版本 | 用途 | 使用 Agent |
|------|------|------|-----------|
| self-improving | 1.2.16 | 自我进化 | 全部 |
| proactive-agent-lite | 1.0.0 | 主动触发 | 全部 |
| openclaw-memory | 1.0.0 | 记忆管理 | 全部 |
| context-scope-tags | 0.2.0 | 上下文增强 | 全部 |
| prompt-enhancer | 1.0.1 | 提示词优化 | 全部 |
| openclaw-skill-vetter | 1.0.0 | 技能审核 | 全部 |
| code-interpreter | 1.0.0 | 代码执行 | 全部 |
| openclaw-tavily-search | 0.1.0 | 搜索服务 | 全部 |
| websearch-free-skill | 0.1.1 | 网页搜索 | 全部 |
| summarize-pro | 1.0.0 | 总结提炼 | 全部 |
| ontology | 1.0.4 | 知识图谱 | 全部 |
| doc-learning | 1.0.0 | 文档学习 | 全部 |
| brainstorming-tazio | 1.0.0 | 头脑风暴 | 全部 |
| runesleo-systematic-debugging | 3.0.0 | 调试 | 全部 |
| feedback-loop | 1.0.0 | 反馈收集 | 全部 |
| test-driven-development | 1.0.0 | 测试驱动 | 全部 |
| playwright-browser-automation | 2.0.0 | 浏览器自动化 | 全部 |
| pdf-ocr-extraction | 1.0.3 | PDF OCR | 全部 |
| excel-xlsx | 1.0.2 | Excel 解析 | 全部 |
| excel-formula | 2.0.1 | Excel 公式 | 全部 |
| word-docx | 1.0.2 | Word 解析 | 全部 |
| generate-excel | 1.0.0 | Excel 生成 | 全部 |
| generate-word-docx | 1.0.0 | Word 生成 | 全部 |
| pptx-generator | 1.0.2 | PPT 生成 | 全部 |

---

## 二、待开发共享技能

| 技能 | 用途 | 优先级 | 负责 |
|------|------|--------|------|
| feishu-doc | 飞书文档操作 | P1 | 待定 |
| web-pilot | 网页自动化 | P1 | 待定 |
| report-generator | 报表生成器 | P2 | Aaron |
| contract-parser | 合同解析器 | P2 | Ella |

---

## 三、共享技能管理规范

### 3.1 安装流程

```bash
# 1. 搜索技能
clawhub search "<关键词>"

# 2. 安全扫描
openclaw skills info <slug>

# 3. 安装技能
openclaw skills install <slug>

# 4. 提交到 GitHub
git add skills/<slug>/
git commit -m "feat(skill): install <slug>"
git push
```

### 3.2 更新流程

```bash
# 检查更新
clawhub update <slug>

# 或更新所有技能
clawhub update --all
```

---

## 四、技能依赖关系

```
L0 核心引擎: self-improving → proactive-agent-lite → memory
L1 安全工具: skill-vetter → skill-creator → code-interpreter
L2 信息获取: tavily → websearch → summarize → ontology → doc-learning
L3 质量保障: debugging → feedback → test-driven
L4 领域技能: Ella(OA/合同) | Oliver(ONES) | Aaron(经营) | Iris(邮件)
```

---

_创建时间: 2026-04-12 15:03 | 版本: v1.0 | 作者: Jerry 🦞_

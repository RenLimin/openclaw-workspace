---
name: release-manager
description: 发布管理技能 - 统一管理所有技能的版本控制、打包、发布、备份等功能
version: v2.0.0-20260402
author: Jerry (主代理)
created: 2026-04-01
updated: 2026-04-02
renamed: version-manager → release-manager
---

# version-manager - 版本管理技能

## 🎯 技能概述

**version-manager** 是 OpenClaw 的通用版本管理技能，为所有其他技能提供统一的版本控制、备份、对比、标记等功能。

**核心原则**: 技能、脚本、模板、配置等所有相关文件必须版本一致

---

## 📦 版本号格式

```
{技能名}-v{主版本}.{次版本}.{修订版}.{日期}

示例:
- contract-clause-v7.2.1-20260401
- report-analyzer-v3.1.0-20260330
- oa-browser-automation-v2.0.3-20260401
```

**版本规则**:
| 版本位 | 含义 | 何时更新 |
|--------|------|----------|
| **主版本** | 重大功能变更 (不兼容) | 架构重构、接口变更 |
| **次版本** | 功能增强 (向后兼容) | 新增功能、改进 |
| **修订版** | Bug 修复 | 修复错误、小改进 |
| **日期** | 训练日期 | YYYYMMDD 格式 |

---

## 🚀 新增功能 (v1.1.0-20260402)

### 整合 GitHub 发布

**发布即备份** — 训练完成后一键发布到 GitHub：

```bash
# 发布技能到 GitHub (自动创建 Release)
version-manager publish-github {skill} v{version}

# 示例
version-manager publish-github contract-clause v7.2.1-20260402
```

**发布流程**:
1. ✅ 生成技能包 (.tar.gz)
2. ✅ 计算 SHA256 校验和
3. ✅ 创建 GitHub Release
4. ✅ 更新发布索引
5. ✅ 清理旧版本 (本地保留 1 个)

### 本地备份策略调整

**保留数量**: 最近 **1 个** 版本 (减轻磁盘压力)

**目录结构**:
```
~/.openclaw/workspace/
├── releases/           # 发布包 (永久保留)
│   └── {skill}-v{version}.tar.gz
└── skills/{skill}/
    └── versions/       # 训练备份 (保留 1 个)
        └── v{old-version}-pre-training/
```

---

## 🔄 训练流程 (强制执行)

```
训练开始
    ↓
1. 检查当前版本号 (cat VERSION)
    ↓
2. 创建训练前备份 (backup)
    ↓
3. 记录训练目标和预期改进
    ↓
4. 执行训练
    ↓
5. 训练后对比 (compare)
    ↓
6. 生成变更日志 (CHANGELOG.md)
    ↓
7. 更新版本号及相关文件 (tag)
    ↓
8. 验证训练成果 (自测)
    ↓
9. 确认无误后标记为稳定版本
    ↓
训练完成
```

---

## 🛠️ API 接口

### Python API

```python
from skills.version_manager import backup, tag, compare, list_versions, clean

# 训练前备份 (强制)
backup_name = backup(
    skill_name="ella",
    training_goal="修复履约类型判断错误",
    include_related=True  # 包含相关脚本、模板
)

# 标记新版本
tag(
    skill_name="ella",
    version="v9.5.0",
    changes={
        "fixed": ["修复履约类型判断错误"],
        "improved": ["优化提取逻辑"],
        "changed": ["更新模板格式"]
    }
)

# 版本对比
diff = compare(
    skill_name="ella",
    old_version="v9.4.0",
    new_version="v9.5.0"
)
print(diff.summary)

# 列出所有版本
versions = list_versions("ella")
print(versions)

# 清理旧版本 (保留最近 3 个)
clean("ella", keep=3)
```

### Bash CLI

```bash
# 训练前备份
bash ~/.openclaw/workspace/skills/version-manager/scripts/manager.sh backup ella "修复履约类型判断"

# 标记新版本
bash ~/.openclaw/workspace/skills/version-manager/scripts/manager.sh tag ella v9.5.0

# 对比版本
bash ~/.openclaw/workspace/skills/version-manager/scripts/manager.sh compare ella v9.4.0 v9.5.0

# 列出所有版本
bash ~/.openclaw/workspace/skills/version-manager/scripts/manager.sh list ella

# 清理旧版本
bash ~/.openclaw/workspace/skills/version-manager/scripts/manager.sh clean ella 3

# 查看状态
bash ~/.openclaw/workspace/skills/version-manager/scripts/manager.sh status ella
```

---

## 📁 文件结构

```
~/.openclaw/workspace/skills/version-manager/
├── SKILL.md                     # 本文件
├── VERSION                      # 当前版本号
├── scripts/
│   ├── manager.sh              # Bash 管理脚本
│   ├── backup.py               # 备份功能
│   ├── tag.py                  # 标记功能
│   ├── compare.py              # 对比功能
│   └── enforce.py              # 强制执行检查
├── rules/
│   └── version-rules.json      # 版本管理规则
├── tests/
│   └── test_version_manager.py # 测试用例
└── versions/                    # 历史版本
    └── v1.0.0-20260401/        # 当前版本
```

---

## ⛔ 禁止行为 (强制执行)

| 行为 | 状态 | 检查机制 |
|------|------|----------|
| **直接覆盖当前版本** | ❌ 禁止 | 训练前检查备份是否存在 |
| **使用历史版本替换** | ❌ 禁止 | 版本号必须递增 |
| **不记录变更日志** | ❌ 禁止 | CHANGELOG.md 必须更新 |
| **相关文件版本不一致** | ❌ 禁止 | tag 时自动检查 |
| **训练后不更新版本号** | ❌ 禁止 | 训练完成检查 |
| **不验证训练成果** | ❌ 禁止 | 必须运行测试用例 |

---

## 🔍 强制执行机制

### 训练前检查

```python
from skills.version_manager import pre_training_check

# 所有智能体训练前必须调用
def training_start(skill_name, training_goal):
    # 强制检查
    pre_training_check(skill_name, training_goal)
    
    # 检查通过后才能继续
    # ... 执行训练
```

### 训练后验证

```python
from skills.version_manager import post_training_verify

# 所有智能体训练后必须调用
def training_end(skill_name, new_version):
    # 强制验证
    post_training_verify(skill_name, new_version)
    
    # 验证通过后才能标记为完成
```

---

## 📊 相关文件版本同步规则

| 文件类型 | 版本同步规则 | 示例 |
|----------|-------------|------|
| **技能核心** | 必须包含版本号 | `SKILL-v7.2.1.md` |
| **脚本文件** | 版本号与技能一致 | `extract-v7.2.1.py` |
| **模板文件** | 版本号与技能一致 | `template-v7.2.1.xlsx` |
| **配置文件** | 版本号与技能一致 | `config-v7.2.1.json` |
| **测试文件** | 版本号与技能一致 | `test-v7.2.1.py` |
| **文档文件** | 版本号与技能一致 | `README-v7.2.1.md` |
| **输出文件** | 版本号与技能一致 | `output-v7.2.1.xlsx` |

---

## 📝 变更日志格式

```markdown
# {skill_name} 变更日志

## v7.2.1 - 2026-04-01

### 修复
- 修复履约类型判断错误 (永久授权 vs 临时授权)
- 修复合同产品服务名称提取不完整问题

### 改进
- 优化合同条款提取逻辑
- 提升解析速度 20%

### 变更
- 更新《民法典》条款模板

### 相关文件
- scripts/extract-contract-v7.2.1.py
- templates/contract-template-v7.2.1.xlsx

---

## v7.2.0 - 2026-03-30
...
```

---

## 🎯 使用示例

### 示例 1: Ella 合同技能训练

```python
# 训练开始
from skills.version_manager import backup, tag, compare

skill = "ella"
goal = "修复履约类型判断错误"

# 1. 训练前备份 (强制)
backup_name = backup(skill, goal)
print(f"已备份：{backup_name}")

# 2. 执行训练...
# ... 修改代码 ...

# 3. 训练后对比
diff = compare(skill, "v9.4.0", "v9.5.0")
print(f"变更文件：{diff.modified_files}")

# 4. 标记新版本 (强制)
tag(
    skill,
    "v9.5.0",
    changes={
        "fixed": ["修复履约类型判断错误"],
        "improved": ["优化提取逻辑"]
    }
)

# 5. 验证
print("✅ 训练完成，版本已更新")
```

### 示例 2: 检查技能状态

```bash
# 查看当前状态
bash ~/.openclaw/workspace/skills/version-manager/scripts/manager.sh status ella

# 输出:
# 技能状态：ella
# 当前版本：v9.5.0
# 历史版本数：3
# 相关文件:
#   - 脚本文件：2
#   - 模板文件：1
#   - 最近输出：5 (7 天内)
```

---

## 📋 规则配置

**文件**: `rules/version-rules.json`

```json
{
  "versionFormat": "v{major}.{minor}.{patch}-{date}",
  "backupRequired": true,
  "changelogRequired": true,
  "testRequired": true,
  "relatedFilesSync": true,
  "minVersionsToKeep": 3,
  "autoClean": false
}
```

---

## 🧪 测试用例

运行测试:
```bash
python3 ~/.openclaw/workspace/skills/version-manager/tests/test_version_manager.py
```

---

## 📚 相关文档

- AGENTS.md - 智能体工作区规范 (包含版本管理规则)
- skills/{skill}/CHANGELOG.md - 各技能变更日志
- scripts/skill-version-manager.sh - 旧版脚本 (已迁移)

---

## 📖 相关文档

- **[VERSION-MANAGEMENT-GUIDE.md](./VERSION-MANAGEMENT-GUIDE.md)** - 完整版本管理指南 ⭐
- [AGENTS.md](../../AGENTS.md) - 智能体行为规范
- [scripts/skill-version-manager.sh](./scripts/skill-version-manager.sh) - 版本管理脚本

---

*版本：v1.1.0-20260402*  
*作者：Jerry (主代理)*  
*创建日期：2026-04-01*  
*更新日期：2026-04-02*

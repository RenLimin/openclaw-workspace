# 📦 智能体团队 — 技能管理规则 v2.0

**生效日期**: 2026-04-11
**适用范围**: 全部域技能和共享工具

---

## 1. 技能定义

技能是智能体团队的 **核心颗粒度**，必须满足：

- **完整性**：包含执行任务所需的全部代码、配置、文档
- **独立性**：不依赖其他技能（共享工具除外，见第 2 节）
- **可验证**：有明确的安装验证步骤
- **可回滚**：有版本号，可回退到任意历史版本

---

## 2. 技能分类

| 分类 | 定义 | 存储位置 | 示例 |
|------|------|----------|------|
| **域技能** | 只属于一个 agent，不被其他 agent 依赖 | `agents/{name}/workspace/skills/` | `contract-approval`、`ones-api` |
| **共享工具** | 通用能力，所有 agent 可引用 | `workspace/skills/` | `feishu-doc`、`web-pilot` |
| **外部技能** | 从 ClawHub/GitHub 安装 | `workspace/skills/` 或 `agents/*/workspace/skills/` | `tavily-search`、`clawhub` |
| **本地技能** | 外部技能经修改后固化为本地的技能 | 同域技能或共享工具 | 定制版 `github`、`web-pilot` |

---

## 3. 技能包结构

每个技能必须是一个完整的目录，包含以下文件：

```
skills/{skill-name}/
├── SKILL.md                # [必需] 技能说明（使用方法、触发条件）
├── VERSION                 # [必需] 当前版本号（语义化版本: X.Y.Z）
├── _meta.json              # [必需] 技能元数据（见第 4 节）
├── DEPENDENCIES.md         # [必需] 依赖清单（见第 5 节）
├── CHANGELOG.md            # [推荐] 版本变更日志
├── README.md               # [推荐] 详细说明
├── scripts/                # [可选] 辅助脚本
├── references/             # [可选] 参考资料
└── main.py / main.js       # [可选] 主执行文件
```

---

## 4. 技能元数据（`_meta.json`）

```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "description": "一句话描述技能功能",
  "category": "domain|shared|external|local",
  "owner": "ella|oliver|aaron|iris|jerry|shared",
  "source": "local|clawhub|github",
  "sourceUrl": "https://clawhub.com/...",
  "installedAt": "2026-04-11",
  "lastUpdated": "2026-04-11",
  "updateCheckEnabled": true,
  "localModifications": false,
  "localModificationsDesc": "",
  "triggers": ["关键词1", "关键词2"],
  "dependencies": ["依赖包名@版本"],
  "healthCheck": "验证命令"
}
```

---

## 5. 依赖清单（`DEPENDENCIES.md`）

每个技能必须明确列出所有依赖：

```markdown
# {Skill Name} 依赖清单

## 系统依赖
| 依赖 | 版本要求 | 安装方式 | 说明 |
|------|----------|----------|------|
| Python | >=3.10 | brew install python | 运行时 |
| Node.js | >=18 | brew install node | 脚本运行 |

## 包依赖
| 包名 | 版本 | 安装命令 | 用途 |
|------|------|----------|------|
| playwright | ^1.40 | pip install playwright | 浏览器自动化 |
| openpyxl | ^3.1 | pip install openpyxl | Excel 读写 |

## 外部服务
| 服务 | 用途 | 凭证位置 | 状态 |
|------|------|----------|------|
| 飞书 API | 文档操作 | Keychain: openclaw-feishu | ✅ 已配置 |

## 其他技能依赖
| 技能名 | 版本 | 类型 | 说明 |
|--------|------|------|------|
| web-pilot | >=1.0 | 共享工具 | 浏览器操作 |

## 安装验证
```bash
# 验证命令
python -c "import playwright; print('OK')"
```
```

---

## 6. 技能生命周期

```
安装/创建 → 验证 → 使用 → 更新检查 → (更新/保持)
                                      ↓
                              已本地修改？ → 是 → 利弊分析 → Rex 审批 → 更新/保持
                                      ↓ 否
                              直接更新 → 验证 → 完成
```

### 6.1 技能训练完成后的独立更新

当某个 agent 的技能完成训练或阶段性训练后，**agent 可自行发起 GitHub 提交**：

```
技能训练完成 / 阶段性训练完成
    │
    ▼
1. 更新 training-memory.md
2. 更新技能 VERSION（如有变更）
3. 更新 _meta.json
4. 确保 DEPENDENCIES.md 完整
5. git add + commit + push（仅自己的文件）
6. 向 Jerry 汇报提交结果
```

**权限**：agent 只能提交自己目录下的文件（见 `github-rules.md` 第 6 节）

---

## 7. 定期更新检查机制

### 7.1 检查频率

| 技能类型 | 检查频率 | 检查方式 | 执行者 |
|----------|----------|----------|--------|
| 外部技能（ClawHub/GitHub） | **每周** | `clawhub` CLI / `gh` API | Jerry |
| 本地技能（已修改的外部技能） | **每周** | 检查上游新版本 | Jerry |
| 域技能（纯本地开发） | 不需要 | N/A | — |
| 共享工具（纯本地开发） | 不需要 | N/A | — |

### 7.2 更新检查流程（外部技能）

```
每周六 09:30（Cron 任务）
    │
    ▼
Jerry 遍历所有外部技能
    │
    ├── 有新版本？
    │   ├── 否 → 记录"已是最新"，结束
    │   │
    │   └── 是 → 检查本地是否有修改
    │       │
    │       ├── 无修改 → 直接更新 → 验证 → 提交 Git
    │       │
    │       └── 有修改 → 生成利弊分析报告 → 等待 Rex 审批
```

### 7.3 更新检查流程（本地技能/已修改的外部技能）

当技能已被本地修改时，**不自动更新**，执行以下流程：

1. **检查上游新版本**：记录新版本号和变更内容
2. **生成利弊分析报告**：

```markdown
# 技能更新评估报告

## 基本信息
- 技能: {skill-name}
- 当前版本: X.Y.Z（已本地修改）
- 上游新版本: X.Y+1.Z
- 检查日期: YYYY-MM-DD

## 上游变更内容
- {列出主要变更点}

## 更新利弊分析

### ✅ 更新收益
- {新功能/修复/性能提升}

### ❌ 更新风险
- {可能丢失本地修改}
- {兼容性问题}
- {需要重新训练/验证}

### 📊 本地修改对比
| 本地修改项 | 上游是否已包含 | 更新后是否冲突 |
|------------|----------------|----------------|
| {修改1} | 否 | 是/否 |
| {修改2} | 是 | 否 |

## 建议
- [ ] 建议更新（本地修改已合并到上游）
- [ ] 建议暂不更新（本地修改重要且上游未包含）
- [ ] 建议更新但需要手动合并

## 审批
- [ ] Rex 审批通过
- [ ] Rex 驳回
- [ ] Rex 要求进一步分析
```

3. **等待 Rex 审批**：
   - 审批通过 → 执行更新 → 手动合并本地修改 → 验证 → 提交
   - 驳回 → 记录原因，下次检查日再评估
   - 要求进一步分析 → Jerry 补充信息后重新提交

---

## 8. 技能安装/卸载规则

### 8.1 安装
- 从 ClawHub 安装: `clawhub install {skill-name}`
- 从 GitHub 安装: 克隆到对应 skills 目录
- 本地创建: 按第 3 节结构创建
- 安装后必须: 验证功能、更新 `_meta.json`、提交 Git

### 8.2 卸载
- 先确认没有其他技能依赖该技能
- 备份当前版本到 `skills/_archive/{skill-name}/`
- 从 `_meta.json` 标记 `uninstalledAt`
- 提交 Git

---

## 9. 版本管理

### 9.1 语义化版本 (SemVer)
- `MAJOR.MINOR.PATCH`（如 2.1.0）
- MAJOR: 不兼容的 API 变更
- MINOR: 向后兼容的功能新增
- PATCH: 向后兼容的问题修复

### 9.2 版本更新规则
- 修复 bug → PATCH +1
- 新增功能 → MINOR +1
- 不兼容变更 → MAJOR +1
- 每次版本变更必须更新 CHANGELOG.md

---

## 10. 技能健康检查

每个技能必须定义健康检查命令：

```json
// _meta.json 中
"healthCheck": "python scripts/health_check.py"
```

Jerry 每周更新检查时同步执行健康检查：
- ✅ 正常 → 记录日志
- ❌ 异常 → 尝试修复 → 3 次失败后上报 Rex

---

*技能管理规则 v2.0 — 2026-04-11 — 技能是核心颗粒度，完整、独立、可追溯*

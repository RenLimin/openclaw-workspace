# Agent 创建框架 v1.0

> **设计目标**: 标准化、自动化、可复用的 Agent 创建流程
> 
> **适用范围**: 新增 Agent 的完整生命周期管理

---

## 一、现状分析

### 1.1 已创建的 Agent

| Agent | 目录 | 注册状态 | 文件完整性 |
|-------|------|---------|-----------|
| **Jerry 🦞** | `~/.openclaw/agents/main/` | ✅ 已注册 (main) | ✅ 完整 |
| **Ella 🦊** | `~/.openclaw/agents/ella/` | ❌ 未注册 | ✅ 完整 |
| **Oliver 🐘** | `~/.openclaw/agents/oliver/` | ❌ 未注册 | ✅ 完整 |
| **Aaron 🦉** | `~/.openclaw/agents/aaron/` | ❌ 未注册 | ✅ 完整 |
| **Iris 🐦‍⬛** | `~/.openclaw/agents/iris/` | ❌ 未注册 | ✅ 完整 |

### 1.2 问题

- **未注册**: 4 个 Agent 未在 OpenClaw 系统中注册
- **手动创建**: 目录结构为手动创建，无标准化流程
- **无模板**: 每次创建需要重复编写相同文件
- **无测试**: 创建后无自动化验证

---

## 二、Agent 创建标准流程

### 2.1 推荐方式：使用 `openclaw agents add`

```bash
# 交互式创建
openclaw agents add ella \
    --agent-dir ~/.openclaw/agents/ella \
    --workspace ~/.openclaw/agents/ella/workspace \
    --model bailian/qwen3.6-plus \
    --bind wecom:default

# 非交互式创建
openclaw agents add oliver \
    --agent-dir ~/.openclaw/agents/oliver \
    --workspace ~/.openclaw/agents/oliver/workspace \
    --model bailian/qwen3.6-plus \
    --non-interactive
```

### 2.2 最小化 Agent 结构

```
~/.openclaw/agents/{name}/
├── agent/
│   └── config.json          # Agent 配置（必填）
├── memory/
│   ├── training-memory.md   # 训练记忆
│   └── YYYY-MM-DD.md        # 每日日志
└── workspace/
    ├── SOUL.md              # 角色定义
    ├── USER.md              # 用户信息
    ├── AGENTS.md            # 团队架构
    ├── TOOLS.md             # 工具配置
    ├── MEMORY.md            # 长期记忆
    ├── skills/              # 专属技能
    └── scripts/             # 自动化脚本
```

### 2.3 配置文件模板

#### config.json
```json
{
  "name": "{AgentName}",
  "emoji": "{Emoji}",
  "role": "{角色描述}",
  "description": "{详细职责描述}",
  "workspace": "~/.openclaw/agents/{name}/workspace",
  "sessions": "~/.openclaw/agents/{name}/sessions",
  "memory": "~/.openclaw/agents/{name}/memory",
  "teamRules": "~/.openclaw/workspace/team-rules/",
  "model": "bailian/qwen3.6-plus"
}
```

#### SOUL.md 模板
```markdown
# SOUL.md - {AgentName} {Emoji}

## 身份
- **名字**: {AgentName}
- **角色**: {角色}
- **Emoji**: {Emoji}

## 核心职责
1. {职责 1}
2. {职责 2}
3. {职责 3}

## 工作原则
- {原则 1}
- {原则 2}

## 外部系统
- **系统名称** — 用途

## 升级规则
- P0（紧急）: ...
- P1（24h）: ...
- P2（常规）: ...
```

---

## 三、自动化创建脚本

### 3.1 Agent 创建器

```bash
#!/bin/bash
# scripts/agent-creator.sh
# 自动化 Agent 创建脚本

set -euo pipefail

AGENT_NAME="${1:?Usage: agent-creator.sh <name> <emoji> <role>}"
AGENT_EMOJI="${2:?Emoji}"
AGENT_ROLE="${3:?Role}"

AGENT_DIR="$HOME/.openclaw/agents/$AGENT_NAME"
WORKSPACE_DIR="$AGENT_DIR/workspace"
MEMORY_DIR="$AGENT_DIR/memory"
SKILLS_DIR="$WORKSPACE_DIR/skills"
SCRIPTS_DIR="$WORKSPACE_DIR/scripts"

echo "🤖 创建 Agent: $AGENT_NAME ($AGENT_EMOJI)"

# 1. 创建目录结构
echo "📁 创建目录结构..."
mkdir -p "$AGENT_DIR/agent"
mkdir -p "$WORKSPACE_DIR"
mkdir -p "$MEMORY_DIR"
mkdir -p "$SKILLS_DIR"
mkdir -p "$SCRIPTS_DIR"

# 2. 创建 config.json
echo "⚙️ 创建配置文件..."
cat > "$AGENT_DIR/agent/config.json" << EOF
{
  "name": "$AGENT_NAME",
  "emoji": "$AGENT_EMOJI",
  "role": "$AGENT_ROLE",
  "description": "Auto-generated agent",
  "workspace": "$WORKSPACE_DIR",
  "sessions": "$AGENT_DIR/sessions",
  "memory": "$MEMORY_DIR",
  "teamRules": "~/.openclaw/workspace/team-rules/",
  "model": "bailian/qwen3.6-plus"
}
EOF

# 3. 创建 SOUL.md
echo "🧠 创建 SOUL.md..."
cat > "$WORKSPACE_DIR/SOUL.md" << EOF
# SOUL.md - $AGENT_NAME $AGENT_EMOJI

## 身份
- **名字**: $AGENT_NAME
- **角色**: $AGENT_ROLE
- **Emoji**: $AGENT_EMOJI

## 核心职责
1. 待定义

## 工作原则
- 准确性优先
- 及时通知
- 保密原则

## 升级规则
- P0: 立即上报 Jerry
- P1: 24h 内处理
- P2: 常规处理
EOF

# 4. 创建 USER.md
echo "👤 创建 USER.md..."
cat > "$WORKSPACE_DIR/USER.md" << EOF
# USER.md - About Rex

- **Name**: Rex
- **GitHub**: RenLimin
- **Timezone**: Asia/Shanghai (GMT+8)
- **语言**: 中文

## 对 $AGENT_NAME 的期望
- 工作准确及时
- 异常情况及时上报
EOF

# 5. 创建 AGENTS.md
echo "👥 创建 AGENTS.md..."
cat > "$WORKSPACE_DIR/AGENTS.md" << EOF
# AGENTS.md - $AGENT_NAME 工作区

## 团队架构

| 智能体 | 职责 | Emoji |
|--------|------|-------|
| Jerry | 主代理 & 团队协调员 | 🦞 |
| Ella | 合同管理 | 🦊 |
| Oliver | 项目管理 | 🐘 |
| Aaron | 经营计划 | 🦉 |
| Iris | 辅助工作 | 🐦‍⬛ |

## 技能清单
| 技能 | 版本 | 状态 |
|------|------|------|
| 待添加 | — | ⏳ |

## 工作区路径
- 技能: \$WORKSPACE_DIR/skills/
- 脚本: \$WORKSPACE_DIR/scripts/
- 记忆: \$MEMORY_DIR/

## 团队规则
遵守 \`~/.openclaw/workspace/team-rules/\` 下所有规则。
EOF

# 6. 创建 TOOLS.md
echo "🛠️ 创建 TOOLS.md..."
cat > "$WORKSPACE_DIR/TOOLS.md" << EOF
# TOOLS.md - $AGENT_NAME 工具配置

## 外部系统
| 系统 | 状态 | 配置项 |
|------|------|--------|
| 待配置 | ⏳ | — |

## 笔记
- 待添加
EOF

# 7. 创建 MEMORY.md
echo "📝 创建 MEMORY.md..."
cat > "$WORKSPACE_DIR/MEMORY.md" << EOF
# MEMORY.md - $AGENT_NAME 长期记忆

## 训练状态
- $(date +%Y-%m-%d): 基础架构搭建完成
- 待完成: Phase 2 技能训练
EOF

# 8. 创建 training-memory.md
echo "📚 创建 training-memory.md..."
cat > "$MEMORY_DIR/training-memory.md" << EOF
# Training Memory - $AGENT_NAME

## 训练日志
- $(date +%Y-%m-%d): Agent 创建完成
EOF

# 9. 注册到 OpenClaw
echo "🔗 注册到 OpenClaw..."
openclaw agents add "$AGENT_NAME" \
    --agent-dir "$AGENT_DIR" \
    --workspace "$WORKSPACE_DIR" \
    --model "bailian/qwen3.6-plus" \
    --non-interactive 2>/dev/null || echo "⚠️ 注册失败，可稍后手动注册"

echo ""
echo "✅ Agent $AGENT_NAME 创建完成!"
echo "   目录: $AGENT_DIR"
echo "   工作区: $WORKSPACE_DIR"
echo ""
echo "下一步:"
echo "  1. 编辑 SOUL.md 定义角色职责"
echo "  2. 添加专属技能到 $SKILLS_DIR/"
echo "  3. 配置外部系统接入"
echo "  4. 开始 Phase 2 训练"
```

### 3.2 Agent 验证脚本

```bash
#!/bin/bash
# scripts/agent-validator.sh
# Agent 创建验证

AGENT_NAME="${1:?Usage: agent-validator.sh <name>}"
AGENT_DIR="$HOME/.openclaw/agents/$AGENT_NAME"
WORKSPACE_DIR="$AGENT_DIR/workspace"

echo "🔍 验证 Agent: $AGENT_NAME"
echo ""

PASS=0
FAIL=0

check() {
    local desc="$1"
    local path="$2"
    if [ -f "$path" ]; then
        echo "  ✅ $desc"
        ((PASS++))
    else
        echo "  ❌ $desc (缺失: $path)"
        ((FAIL++))
    fi
}

echo "=== 目录结构 ==="
[ -d "$AGENT_DIR" ] && echo "  ✅ 主目录" || echo "  ❌ 主目录"
[ -d "$AGENT_DIR/agent" ] && echo "  ✅ agent/" || echo "  ❌ agent/"
[ -d "$WORKSPACE_DIR" ] && echo "  ✅ workspace/" || echo "  ❌ workspace/"
[ -d "$AGENT_DIR/memory" ] && echo "  ✅ memory/" || echo "  ❌ memory/"
[ -d "$WORKSPACE_DIR/skills" ] && echo "  ✅ skills/" || echo "  ❌ skills/"
[ -d "$WORKSPACE_DIR/scripts" ] && echo "  ✅ scripts/" || echo "  ❌ scripts/"

echo ""
echo "=== 核心文件 ==="
check "config.json" "$AGENT_DIR/agent/config.json"
check "SOUL.md" "$WORKSPACE_DIR/SOUL.md"
check "USER.md" "$WORKSPACE_DIR/USER.md"
check "AGENTS.md" "$WORKSPACE_DIR/AGENTS.md"
check "TOOLS.md" "$WORKSPACE_DIR/TOOLS.md"
check "MEMORY.md" "$WORKSPACE_DIR/MEMORY.md"
check "training-memory.md" "$AGENT_DIR/memory/training-memory.md"

echo ""
echo "=== 注册状态 ==="
if openclaw agents list 2>/dev/null | grep -q "$AGENT_NAME"; then
    echo "  ✅ 已注册"
    ((PASS++))
else
    echo "  ❌ 未注册"
    ((FAIL++))
fi

echo ""
echo "=== 验证结果 ==="
echo "通过: $PASS | 失败: $FAIL"

if [ $FAIL -eq 0 ]; then
    echo "✅ Agent 验证通过!"
    exit 0
else
    echo "❌ Agent 验证失败，请检查缺失项"
    exit 1
fi
```

---

## 四、Agent 注册与绑定

### 4.1 注册现有 Agent

```bash
# 注册 Ella
openclaw agents add ella \
    --agent-dir ~/.openclaw/agents/ella \
    --workspace ~/.openclaw/agents/ella/workspace \
    --model bailian/qwen3.6-plus \
    --non-interactive

# 注册 Oliver
openclaw agents add oliver \
    --agent-dir ~/.openclaw/agents/oliver \
    --workspace ~/.openclaw/agents/oliver/workspace \
    --model bailian/qwen3.6-plus \
    --non-interactive

# 注册 Aaron
openclaw agents add aaron \
    --agent-dir ~/.openclaw/agents/aaron \
    --workspace ~/.openclaw/agents/aaron/workspace \
    --model bailian/qwen3.6-plus \
    --non-interactive

# 注册 Iris
openclaw agents add iris \
    --agent-dir ~/.openclaw/agents/iris \
    --workspace ~/.openclaw/agents/iris/workspace \
    --model bailian/qwen3.6-plus \
    --non-interactive
```

### 4.2 路由绑定

```bash
# 绑定企业微信到 Jerry
openclaw agents bind --agent jerry --bind wecom:default

# 绑定 ClawChat 到 Jerry
openclaw agents bind --agent jerry --bind openclawwechat:default

# 查看所有绑定
openclaw agents bindings
```

---

## 五、推荐技能与规则

### 5.1 每个 Agent 必备

| 技能/文件 | 用途 | 状态 |
|----------|------|------|
| SOUL.md | 角色定义 | ✅ 已创建 |
| USER.md | 用户信息 | ✅ 已创建 |
| AGENTS.md | 团队架构 | ✅ 已创建 |
| TOOLS.md | 工具配置 | ✅ 已创建 |
| MEMORY.md | 长期记忆 | ✅ 已创建 |
| training-memory.md | 训练记忆 | ✅ 已创建 |

### 5.2 共享规则

所有 Agent 遵守 `~/.openclaw/workspace/team-rules/` 下的规则：

| 规则文件 | 内容 |
|---------|------|
| general-rules.md | 通用行为准则 |
| security-rules.md | 安全规范 |
| training-rules.md | 训练规范 |
| github-rules.md | Git 操作规范 |
| skill-rules.md | 技能管理规则 |
| network-rules.md | 网络代理规则 |
| environment-config.md | 环境配置 |
| skill-training-framework.md | 训练框架 |

### 5.3 Agent 专属技能

| Agent | 技能 | 说明 |
|-------|------|------|
| Ella 🦊 | oa-approval | OA 审批 |
| Ella 🦊 | contract-management | 合同管理 |
| Oliver 🐘 | ones-integration | ONES 操作 |
| Aaron 🦉 | business-analysis | 经营分析 |
| Iris 🐦‍⬛ | email-management | 邮件管理 |

---

## 六、最佳实践

### 6.1 命名规范

- **Agent 名称**: 简短、易记、有意义 (如 Ella, Oliver)
- **Emoji**: 唯一标识，用于视觉区分
- **目录名**: 小写、无空格 (如 `ella`, `oliver`)

### 6.2 职责划分

- **高内聚**: 每个 Agent 专注一个领域
- **低耦合**: Agent 间通过 Jerry 协调，不直接依赖
- **可替代**: 每个 Agent 的职责可独立替换

### 6.3 安全原则

- **最小权限**: 每个 Agent 只有所需的最小权限
- **凭证隔离**: 每个 Agent 的凭证独立存储
- **操作审计**: 所有外部操作记录日志

### 6.4 维护规范

- **每日日志**: 记录在 `memory/YYYY-MM-DD.md`
- **长期记忆**: 重要事件更新到 `MEMORY.md`
- **技能更新**: 新技能添加到 AGENTS.md
- **定期备份**: 工作区定期推送到 GitHub

---

## 七、执行计划

### 7.1 立即执行

| 步骤 | 操作 | 状态 |
|------|------|------|
| 1 | 创建 agent-creator.sh | ⏳ |
| 2 | 创建 agent-validator.sh | ⏳ |
| 3 | 注册 4 个 Agent 到 OpenClaw | ⏳ |
| 4 | 验证所有 Agent | ⏳ |

### 7.2 后续优化

| 步骤 | 操作 | 状态 |
|------|------|------|
| 5 | 配置路由绑定 | ⏳ |
| 6 | 添加 Agent 监控 | ⏳ |
| 7 | 创建 Agent 健康检查 | ⏳ |

---

_创建时间: 2026-04-12 14:32 | 版本: v1.0 | 作者: Jerry 🦞_

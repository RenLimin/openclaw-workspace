# 🔒 智能体团队 — 安全规则 v2.0

**生效日期**: 2026-04-11
**适用范围**: 全部 5 个智能体

---

## 1. 凭证管理

- **所有敏感凭证**（API Key、Token、密码）只存储在 macOS Keychain 中
- **禁止**将凭证明文写入任何文件
- **禁止**将凭证提交到 Git
- Keychain 条目命名规范: `openclaw-{service}`（如 `openclaw-ones`, `openclaw-oa`, `openclaw-email`）
- `.gitignore` 必须包含：`*.key`, `*.secret`, `*.env`, `config/openclaw.json`（如含敏感信息）

## 2. 外部操作安全

### 2.1 需要 Rex 确认后才能执行
- 发送邮件
- 发布到外部平台（GitHub PR、企业微信通知等）
- 删除或覆盖生产数据
- 修改系统配置
- 调用涉及资金的 API

### 2.2 可自主执行
- 读取文件、查询数据
- 本地文件操作（创建、编辑、整理）
- Git 提交到备份仓库
- 记忆更新

## 3. 数据安全

- **生产数据定义**: 合同数据库、ONES 数据、OA 审批数据 = 生产数据，禁止覆盖
- **测试数据**: 训练中的模拟数据不属于生产数据，可自由操作
- **数据库文件**（*.sqlite）不进入 Git
- **会话记录**（*.jsonl）只进入备份仓库，不进 workspace
- **个人隐私数据**不写入 MEMORY.md
- 合同、财务等敏感数据加密或限制访问

## 4. GitHub 安全

- 使用 PAT (Personal Access Token)，不用账号密码
- Token 只存 Keychain，环境变量动态注入
- `git push` 前确认目标分支
- 禁止 force push 到 main

## 5. 浏览器安全

- 每个 agent 使用独立的 Chrome profile
- 会话结束后清理浏览器状态（如需要）
- 不在浏览器中输入与任务无关的敏感信息
- 浏览器操作后清理 cookie，不在页面中保存密码
- 敏感页面（登录、审批确认）操作后截图留档
- 禁止在浏览器中访问与工作无关的网站

## 6. 审计

- 所有外部操作记录日志
- 日志文件: `~/.openclaw/logs/{agent-name}.log`
- 定期 review 日志，发现异常立即上报 Jerry

---

*安全规则 v2.0 — 2026-04-11 更新 — 宁可多做确认，不可冒进*

# 🖥️ 智能体团队 — 系统环境配置 v2.0

**生效日期**: 2026-04-11
**适用范围**: 全部 5 个智能体的训练和执行环境

---

## 1. 主机信息

| 项目 | 值 |
|------|-----|
| 主机名 | bangcle的MacBook Pro |
| 型号 | Mac (MacIntel) |
| 操作系统 | macOS 26.4.1 (Sequoia) |
| 架构 | x64 |
| 用户 | bangcle |
| 时区 | Asia/Shanghai (GMT+8) |

## 2. 运行环境

| 项目 | 版本 | 说明 |
|------|------|------|
| Node.js | v25.6.1 | OpenClaw 运行时 |
| OpenClaw | 2026.4.10 | 主框架 |
| Shell | zsh | 默认 shell |
| Python | _(待确认)_ | 技能脚本可能需要 |
| Git | _(待确认)_ | 版本管理 |

## 3. 办公软件

| 软件 | 版本 | 用途 |
|------|------|------|
| **Microsoft Office 365** | _(待确认)_ | Word、Excel、PPT 操作 |
| 飞书 | _(待确认)_ | 飞书文档 API 集成 |
| Chrome | _(待确认)_ | 浏览器自动化 (Playwright) |

## 4. 外部系统集成

| 系统 | 类型 | 默认值 | 凭证位置 |
|------|------|--------|----------|
| **泛微 OA** | OA 审批 | 默认 OA 系统 | Keychain: `openclaw-oa` |
| **万事 ONES** | 项目管理 | 默认项目管理系统 | Keychain: `openclaw-ones` |
| 网易邮箱 | 邮件 | 默认邮箱 | Keychain: `openclaw-email` |
| 企业微信 | 通讯 | 默认通讯工具 | Keychain: `openclaw-wechat` |
| GitHub | 代码托管 | `RenLimin/openclaw-workspace` | Keychain: `gh:github.com` |
| 百炼 (DashScope) | 模型 | `bailian/qwen3.6-plus` | openclaw.json |

## 5. 网络代理

| 项目 | 值 | 说明 |
|------|-----|------|
| 备份代理 | `http://127.0.0.1:7897` | 默认关闭，直连失败时启用 |
| Clash Verge | `/Applications/Clash Verge.app` | 代理客户端，需手动启动 |
| Clash 配置端口 | mixed-port: 7890 | 实际代理端口 |

### 代理启用步骤
1. 启动 Clash Verge (`/Applications/Clash Verge.app`)
2. 确认代理端口 (7890 或 7897)
3. 设置 Git 代理: `git config --global http.proxy http://127.0.0.1:7890`
4. 测试: `curl -x http://127.0.0.1:7890 https://api.github.com`

## 6. 浏览器配置

| 项目 | 值 |
|------|-----|
| 默认浏览器 | Chrome |
| Playwright | 用于浏览器自动化 |
| Agent 独立 Profile | `~/.openclaw/browser/{ella,oliver,oscar}/` |

## 7. 数据库

| 数据库 | 用途 | 位置 |
|--------|------|------|
| contract-management.sqlite | 合同数据 | `~/.openclaw/memory/` |
| report-analyzer.sqlite | 报告数据 | `~/.openclaw/memory/` |
| ones-project.sqlite | ONES 数据 | `~/.openclaw/memory/` |
| email.sqlite | 邮件数据 | `~/.openclaw/memory/` |
| oa-agent.sqlite | OA 数据 | `~/.openclaw/memory/` |
| main.sqlite | 主记忆 | `~/.openclaw/memory/` |

## 8. 待确认项

- [ ] Python 版本 (`python3 --version`)
- [ ] Microsoft Office 365 具体版本
- [ ] Chrome 版本
- [ ] 飞书桌面应用版本
- [ ] 各外部系统的 API 版本

---

*系统环境配置 v2.0 — 2026-04-11 — 训练和执行的环境基准*

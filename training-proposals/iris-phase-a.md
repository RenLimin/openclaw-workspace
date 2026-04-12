# 训练方案: Iris 🐦‍⬛ 邮件管理 + 智能体万能助手 (Agent Loop)

> **生成时间**: 2026-04-12 19:45
> **基于**: `/Users/bangcle/Downloads/openclaw-skill/训练计划-20260412.md`
> **生成者**: Jerry 🦞 (代 Iris 生成)

---

## 一、训练目标

1. **邮件管理**: 通过 Keychain 获取客户端授权码，配置邮箱接入
2. **Agent Loop 应用**: 验证持续循环执行能力，作为团队万能助手

---

## 二、输入数据/环境

### 训练任务来源
- **文件**: `/Users/bangcle/Downloads/openclaw-skill/训练计划-20260412.md`
- **邮箱地址**: `limin.ren@bangcle.com`
- **凭证来源**: Keychain 客户端授权码

### 当前环境
| 项目 | 状态 | 说明 |
|------|------|------|
| 邮箱地址 | ✅ 已知 | `limin.ren@bangcle.com` |
| Keychain 授权码 | ⏳ 待确认 | 需要存储到 Keychain |
| IMAP/SMTP 服务器 | ⏳ 待确认 | 需要根据邮箱服务商确定 |
| iris-loop.py | ✅ 已安装 | v2.0 (含自进化) |
| 浏览器环境 | ✅ 已配置 | `~/.openclaw/browser-data/iris/` |

### 可用技能
| 技能 | 用途 |
|------|------|
| email-management | 邮件管理 |
| openclaw-tavily-search | 邮件服务商配置检索 |
| websearch-free-skill | 补充信息检索 |
| summarize-pro | 邮件摘要 |
| playwright-browser-automation | 网页邮箱操作 |
| self-improving | 自进化复盘 |
| iris-loop.py | Agent Loop 脚本 |

---

## 三、执行步骤

### 任务 1: 邮箱配置

| 步骤 | 操作 | 使用技能 | 预期输出 |
|------|------|---------|---------|
| 1.1 | 检查 Keychain 授权码 | security CLI | 获取授权码 |
| 1.2 | 检索邮箱服务商配置 | openclaw-tavily-search | IMAP/SMTP 服务器地址 |
| 1.3 | 存储凭证到 Keychain | security CLI | 凭证持久化 |
| 1.4 | 测试 IMAP 连接 | code-interpreter (imaplib) | 连接成功 |
| 1.5 | 测试 SMTP 连接 | code-interpreter (smtplib) | 连接成功 |

### 任务 2: Agent Loop 验证

| 步骤 | 操作 | 使用技能 | 预期输出 |
|------|------|---------|---------|
| 2.1 | 检查 iris-loop.py 配置 | read | 确认配置正确 |
| 2.2 | 启动 Loop 脚本 | iris-loop.py | Loop 运行日志 |
| 2.3 | 验证邮件检查任务 | email-management | 邮件分类结果 |
| 2.4 | 验证系统监控任务 | code-interpreter | 系统状态报告 |
| 2.5 | 验证自进化审查 | self-improving | 自进化报告 |
| 2.6 | 验证技术瓶颈研究 | tavily-search, code-interpreter | 研究方案 |
| 2.7 | 优化 Loop 配置 | self-improving | 优化后的配置 |

---

## 四、风险评估

| 风险 | 可能性 | 应对方案 |
|------|--------|---------|
| Keychain 无邮箱授权码 | 高 | 请 Rex 提供并存储 |
| IMAP/SMTP 服务器地址未知 | 中 | 检索邮箱服务商配置 |
| 邮箱服务商限制 IMAP | 中 | 使用网页邮箱 (Playwright) 替代 |
| Loop 脚本异常 | 低 | 已有错误处理机制 |

---

## 五、不确定项

- [ ] 需要 Rex 存储：邮箱客户端授权码到 Keychain
  ```bash
  security add-generic-password -s "openclaw-browser-iris-email-username" -a "iris" -w "limin.ren@bangcle.com" -U
  security add-generic-password -s "openclaw-browser-iris-email-password" -a "iris" -w "<授权码>" -U
  ```
- [ ] 需要确认：邮箱服务商 (网易/QQ/企业微信邮箱？)
- [ ] 需要确认：IMAP/SMTP 服务器地址和端口

---

## 六、验收标准

- [ ] 能从 Keychain 获取邮箱授权码
- [ ] 能检索并确认 IMAP/SMTP 服务器配置
- [ ] 能成功测试 IMAP 连接
- [ ] 能成功测试 SMTP 连接
- [ ] iris-loop.py 能正常启动和循环执行
- [ ] 能完成邮件检查任务
- [ ] 能完成自进化审查
- [ ] 能完成技术瓶颈研究
- [ ] 所有测试过程记录到 memory
- [ ] self-improving 复盘完成

---

_生成者: Jerry 🦞 (代 Iris)_

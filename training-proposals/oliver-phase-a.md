# 训练方案: Oliver 🐘 项目管理 + 万事 ONES 浏览器自动化

> **生成时间**: 2026-04-12 19:45
> **基于**: `/Users/bangcle/Downloads/openclaw-skill/训练计划-20260412.md`
> **生成者**: Jerry 🦞 (代 Oliver 生成)

---

## 一、训练目标

1. **万事 ONES 浏览器自动化**: 通过 Keychain 获取凭证，自动登录 ONES 系统
2. **ONES 系统解析**: 解读 ONES 系统结构，输出可支持的自动化操作清单

---

## 二、输入数据/环境

### 训练任务来源
- **文件**: `/Users/bangcle/Downloads/openclaw-skill/训练计划-20260412.md`
- **参考数据**: `/Users/bangcle/Downloads/ones` (ONES 系统截图/文档)
- **前置权限**: ONES 普通账号

### 当前环境
| 项目 | 状态 | 说明 |
|------|------|------|
| Keychain 凭证 | ⏳ 待确认 | `openclaw-browser-oliver-ones-*` |
| ONES 系统地址 | ⏳ 待提供 | ONES 系统 URL |
| 参考数据目录 | ✅ 待检查 | `/Users/bangcle/Downloads/ones` |
| 浏览器环境 | ✅ 已配置 | `~/.openclaw/browser-data/oliver/` |
| Playwright | ✅ 已安装 | 1.58.0 |

### 可用技能
| 技能 | 用途 |
|------|------|
| playwright-browser-automation | 浏览器自动化 |
| dynamic-browser-engine | 动态页面引擎 v3.0 |
| openclaw-tavily-search | ONES API 文档检索 |
| summarize-pro | 系统文档摘要 |
| excel-xlsx | 操作清单导出 |
| ontology | 系统结构知识图谱 |
| self-improving | 自进化复盘 |

---

## 三、执行步骤

### 任务 1: 万事 ONES 登录

| 步骤 | 操作 | 使用技能 | 预期输出 |
|------|------|---------|---------|
| 1.1 | 检查 Keychain 凭证 | security CLI | 获取账号密码 |
| 1.2 | 启动浏览器 | playwright-browser-automation | Oliver 专属浏览器 |
| 1.3 | 导航到 ONES 登录页 | playwright | 登录页面 |
| 1.4 | 自动填写凭证 | playwright (fill + click) | 登录成功 |
| 1.5 | 保存 Cookie | playwright context | Cookie 持久化 |

### 任务 2: ONES 系统解析

| 步骤 | 操作 | 使用技能 | 预期输出 |
|------|------|---------|---------|
| 2.1 | 检查参考数据 | read + code-interpreter | 分析 `/Users/bangcle/Downloads/ones` |
| 2.2 | 导航 ONES 各模块 | playwright | 模块列表 |
| 2.3 | 解析菜单结构 | playwright (evaluate) | 系统菜单 JSON |
| 2.4 | 识别可操作页面 | playwright + 视觉识别 | 页面功能清单 |
| 2.5 | 提取 API 信息 | playwright + tavily-search | API 端点清单 |
| 2.6 | 构建系统知识图谱 | ontology | ONES 系统结构图谱 |
| 2.7 | 输出自动化操作清单 | excel-xlsx, generate-excel | `可支持的自动化操作清单.xlsx` |

---

## 四、风险评估

| 风险 | 可能性 | 应对方案 |
|------|--------|---------|
| Keychain 无 ONES 凭证 | 高 | 请 Rex 提供凭证并存储 |
| ONES 系统需要二次验证 | 中 | 使用视觉识别或请求 Rex 协助 |
| 参考数据目录为空 | 中 | 直接通过浏览器探索 |
| 普通账号权限不足 | 中 | 先提取可访问的模块信息 |

---

## 五、不确定项

- [ ] 需要 Rex 提供：万事 ONES 系统 URL
- [ ] 需要 Rex 存储：ONES 账号密码到 Keychain
  ```bash
  security add-generic-password -s "openclaw-browser-oliver-ones-username" -a "oliver" -w "<账号>" -U
  security add-generic-password -s "openclaw-browser-oliver-ones-password" -a "oliver" -w "<密码>" -U
  ```
- [ ] 需要确认：`/Users/bangcle/Downloads/ones` 目录内容

---

## 六、验收标准

- [ ] 能通过 Keychain 凭证自动登录万事 ONES
- [ ] 能解析 ONES 系统菜单结构
- [ ] 能识别所有可操作页面
- [ ] 能提取 API 端点信息
- [ ] 能构建 ONES 系统知识图谱
- [ ] 能输出 `可支持的自动化操作清单.xlsx`
- [ ] 所有测试过程记录到 memory
- [ ] self-improving 复盘完成

---

_生成者: Jerry 🦞 (代 Oliver)_

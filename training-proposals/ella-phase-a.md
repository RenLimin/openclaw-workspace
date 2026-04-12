# 训练方案: Ella 🦊 合同管理 + 泛微 OA 浏览器自动化

> **生成时间**: 2026-04-12 19:45
> **基于**: `/Users/bangcle/Downloads/openclaw-skill/训练计划-20260412.md`
> **生成者**: Jerry 🦞 (代 Ella 生成)

---

## 一、训练目标

1. **泛微 OA 浏览器自动化**: 通过 Keychain 获取凭证，自动登录泛微 OA 系统
2. **合同信息提取**: 从 OA 系统提取合同附件和分项记录，导出为 CSV
3. **合同法规解读**: 搜索《民法典》等法规，输出合同条款结构和合规标准

---

## 二、输入数据/环境

### 训练任务来源
- **文件**: `/Users/bangcle/Downloads/openclaw-skill/训练计划-20260412.md`
- **前置权限**: 泛微 OA 普通账号

### 当前环境
| 项目 | 状态 | 说明 |
|------|------|------|
| Keychain 凭证 | ⏳ 待确认 | `openclaw-browser-ella-oa-*` |
| 泛微 OA 地址 | ⏳ 待提供 | OA 系统 URL |
| 浏览器环境 | ✅ 已配置 | `~/.openclaw/browser-data/ella/` |
| Playwright | ✅ 已安装 | 1.58.0 |

### 可用技能
| 技能 | 用途 |
|------|------|
| playwright-browser-automation | 浏览器自动化 |
| dynamic-browser-engine | 动态页面引擎 v3.0 |
| openclaw-tavily-search | 法规检索 |
| summarize-pro | 法规摘要 |
| excel-xlsx | CSV 导出 |
| word-docx | 合同文档处理 |
| self-improving | 自进化复盘 |

---

## 三、执行步骤

### 任务 1: 泛微 OA 登录

| 步骤 | 操作 | 使用技能 | 预期输出 |
|------|------|---------|---------|
| 1.1 | 检查 Keychain 凭证 | security CLI | 获取账号密码 |
| 1.2 | 启动浏览器 | playwright-browser-automation | Ella 专属浏览器 |
| 1.3 | 导航到 OA 登录页 | playwright | 登录页面 |
| 1.4 | 自动填写凭证 | playwright (fill + click) | 登录成功 |
| 1.5 | 保存 Cookie | playwright context | Cookie 持久化 |

### 任务 2: OA 合同信息查询

| 步骤 | 操作 | 使用技能 | 预期输出 |
|------|------|---------|---------|
| 2.1 | 进入合同查询模块 | playwright | 合同列表页 |
| 2.2 | 解析合同列表 | playwright (evaluate) | 合同信息 JSON |
| 2.3 | 提取合同附件 | playwright (download) | 合同附件原文 |
| 2.4 | 提取分项记录 | playwright (evaluate) | 分项数据 |
| 2.5 | 导出 CSV | excel-xlsx, pandas | `合同分项导出数据.csv` |

### 任务 3: 合同法规解读

| 步骤 | 操作 | 使用技能 | 预期输出 |
|------|------|---------|---------|
| 3.1 | 搜索《民法典》合同相关 | openclaw-tavily-search | 法规原文 |
| 3.2 | 法规解读 | summarize-pro | 条款解读摘要 |
| 3.3 | 提取条款结构 | summarize-pro, code-interpreter | 合同条款结构 |
| 3.4 | 生成 Excel 模版 | excel-xlsx, generate-excel | 合同合规检查表 |
| 3.5 | 合规判断标准 | self-improving, brainstorming-tazio | 合规判断标准文档 |

---

## 四、风险评估

| 风险 | 可能性 | 应对方案 |
|------|--------|---------|
| Keychain 无 OA 凭证 | 高 | 请 Rex 提供凭证并存储 |
| OA 系统需要验证码 | 中 | 使用视觉识别或请求 Rex 协助 |
| 合同附件下载权限不足 | 中 | 先提取可访问的列表信息 |
| 法规检索结果不准确 | 低 | 多引擎检索 + 人工校验 |

---

## 五、不确定项

- [ ] 需要 Rex 提供：泛微 OA 系统 URL
- [ ] 需要 Rex 存储：OA 账号密码到 Keychain
  ```bash
  security add-generic-password -s "openclaw-browser-ella-oa-username" -a "ella" -w "<账号>" -U
  security add-generic-password -s "openclaw-browser-ella-oa-password" -a "ella" -w "<密码>" -U
  ```
- [ ] 需要确认：合同信息查询的具体模块路径

---

## 六、验收标准

- [ ] 能通过 Keychain 凭证自动登录泛微 OA
- [ ] 能提取合同附件原文
- [ ] 能导出 `合同分项导出数据.csv`
- [ ] 能搜索并解读《民法典》合同相关条款
- [ ] 能生成合同条款结构文档
- [ ] 能生成合同合规检查 Excel 模板
- [ ] 能输出合同条款合规判断标准
- [ ] 所有测试过程记录到 memory
- [ ] self-improving 复盘完成

---

_生成者: Jerry 🦞 (代 Ella)_

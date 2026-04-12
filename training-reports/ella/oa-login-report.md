# 泛微 OA 浏览器自动化测试报告

> **测试时间**: 2026-04-12 21:40
> **测试者**: Ella 🦊

---

## 一、测试结果

| 测试项 | 结果 | 说明 |
|--------|------|------|
| OA URL 访问 | ⚠️ 部分成功 | oa.bangcle.com 返回 200，但重定向到 IAM |
| IAM 登录 | ❌ 失败 | IAM 页面在 headless 模式下超时 |
| 浏览器类型 | Firefox | Chromium 也失败 |
| 超时时间 | 120s | 仍然超时 |

---

## 二、问题分析

### 2.1 访问流程
```
oa.bangcle.com → 重定向到 → iam.bangcle.com → 登录页 → OA 主页
```

### 2.2 失败原因
- IAM 系统可能有反爬虫检测
- Headless 浏览器被识别并阻止
- 页面加载时间过长 (>120s)

### 2.3 可行方案
1. **非 headless 模式**: 使用有头浏览器手动登录后保存 Cookie
2. **Cookie 注入**: 手动登录后导出 Cookie，自动化脚本使用 Cookie
3. **API 登录**: 如果 IAM 提供登录 API，直接使用 API

---

## 三、推荐方案

### 方案 A: Cookie 注入 (推荐)
1. 手动登录 IAM 系统
2. 导出 Cookie 到文件
3. 自动化脚本加载 Cookie 访问 OA

### 方案 B: 非 headless 模式
1. 使用有头浏览器
2. 手动输入验证码 (如有)
3. 自动化后续操作

---

## 四、下一步

1. Rex 手动登录 IAM 并导出 Cookie
2. 或提供 IAM 登录 API 端点
3. 或使用非 headless 模式测试

---

_测试者: Ella 🦊_

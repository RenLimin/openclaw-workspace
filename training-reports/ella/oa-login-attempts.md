# 泛微 OA 浏览器自动化 - 完整测试报告

> **测试时间**: 2026-04-12 21:50
> **测试者**: Ella 🦊

---

## 一、测试结果汇总

| 测试项 | 浏览器 | 结果 | 说明 |
|--------|--------|------|------|
| OA 直接访问 | Firefox | ⚠️ 重定向 | 重定向到 IAM 登录页 |
| OA 直接访问 | Chromium | ❌ 超时 | >120s 超时 |
| IAM 登录 | Firefox | ❌ 无输入框 | 页面未渲染表单 |
| IAM 登录 | Chromium | ❌ 超时 | >120s 超时 |
| 网络连通性 | - | ✅ 200 | OA 和 IAM 都可访问 |

---

## 二、问题分析

### 2.1 根本原因
IAM 系统 (`iam.bangcle.com`) 在 headless 浏览器模式下：
- 页面加载超时 (>120s)
- 即使加载成功，表单元素也不渲染
- 可能原因：反爬虫检测、JavaScript 执行被阻止

### 2.2 尝试的方案
| 方案 | 结果 |
|------|------|
| Chromium headless | ❌ 超时 |
| Firefox headless | ❌ 表单不渲染 |
| 延长超时到 120s | ❌ 仍然超时 |
| 等待 domcontentloaded | ❌ 超时 |
| 等待 networkidle | ❌ 超时 |
| 直接等待 10s | ❌ 无输入框 |

---

## 三、推荐解决方案

### 方案 A: Cookie 注入 (推荐)
1. **手动登录**: Rex 在浏览器中手动登录 IAM 系统
2. **导出 Cookie**: 使用浏览器开发者工具导出 Cookie
3. **Cookie 注入**: 自动化脚本加载 Cookie 访问 OA

**导出 Cookie 步骤**:
```
1. 浏览器访问 https://iam.bangcle.com/
2. 手动输入账号 limin.ren 和密码 June-123
3. 登录成功后，按 F12 打开开发者工具
4. Application/Storage → Cookies → https://iam.bangcle.com
5. 导出所有 Cookie 为 JSON 文件
```

### 方案 B: 非 headless 模式
- 需要显示器环境
- 手动处理验证码 (如有)
- 自动化后续操作

### 方案 C: 使用 OA API
- 如果 OA 提供 API 接口
- 直接通过 API 获取数据
- 无需浏览器自动化

---

## 四、下一步行动

1. **Rex 手动登录 IAM** 并导出 Cookie
2. 提供 Cookie 文件或 IAM API 端点
3. 或使用非 headless 模式测试

---

_测试者: Ella 🦊_

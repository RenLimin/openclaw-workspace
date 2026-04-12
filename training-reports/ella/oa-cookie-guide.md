# 泛微 OA Cookie 导出指南

> **生成时间**: 2026-04-12 22:40
> **生成者**: Jerry 🦞

---

## 一、已尝试方案汇总

| 方案 | 浏览器 | 结果 | 说明 |
|------|--------|------|------|
| Chromium headless | Chrome | ❌ 超时 >120s | IAM 页面不响应 |
| Firefox headless | Firefox | ❌ 表单不渲染 | 输入框数量为 0 |
| Stealth 模式 (args) | Chrome | ❌ 超时 | 反爬虫检测 |
| Stealth 模式 (init_script) | Chrome | ❌ 超时 | 移除 webdriver 无效 |
| 延长超时 120s | 两者 | ❌ 超时 | 网络正常但页面不加载 |
| 不同 wait_until | 两者 | ❌ 超时 | domcontentloaded/load 均失败 |

### 技术分析
- **网络连通性**: ✅ OA 和 IAM 都返回 200
- **页面响应**: ❌ Headless 模式下 IAM 不渲染表单
- **可能原因**: IAM 系统使用高级反爬虫检测 (如 Cloudflare、自定义指纹)

---

## 二、手动导出 Cookie 步骤

### 步骤 1: 登录 IAM 系统

1. 打开浏览器访问: **https://iam.bangcle.com/**
2. 输入账号: `limin.ren`
3. 输入密码: `June-123`
4. 点击 **Login** 登录

### 步骤 2: 确认登录成功

登录后页面应跳转到 OA 系统:
- URL 应包含: `https://oa.bangcle.com/wui/index.html`
- 页面标题: "泛微-协同管理云平台"

### 步骤 3: 导出 Cookie

#### Chrome/Edge 浏览器:
1. 按 **F12** 打开开发者工具
2. 点击 **Application** (应用) 标签
3. 左侧展开 **Cookies** → 选择 `https://iam.bangcle.com`
4. 右键点击任意 Cookie → **Export all** (导出全部)
5. 保存为 `iam-cookies.json`

#### Firefox 浏览器:
1. 按 **F12** 打开开发者工具
2. 点击 **Storage** (存储) 标签
3. 左侧展开 **Cookies** → 选择 `https://iam.bangcle.com`
4. 右键点击 → **Export All** (导出全部)
5. 保存为 `iam-cookies.json`

### 步骤 4: 提供 Cookie 文件

将 `iam-cookies.json` 文件保存到:
```
/Users/bangcle/.openclaw/workspace/training-reports/ella/iam-cookies.json
```

---

## 三、Cookie 文件格式

导出的 JSON 格式应类似:
```json
[
  {
    "name": "JSESSIONID",
    "value": "xxxxx",
    "domain": ".bangcle.com",
    "path": "/",
    "secure": true,
    "httpOnly": true
  },
  ...
]
```

---

## 四、自动化脚本使用 Cookie

收到 Cookie 后，Ella 的自动化脚本将:
1. 加载 Cookie 到浏览器上下文
2. 直接访问 OA 系统 (无需登录)
3. 执行合同信息查询和提取
4. 导出 CSV 数据

---

## 五、注意事项

1. **Cookie 有效期**: 通常 2-24 小时，导出后尽快使用
2. **安全**: Cookie 包含会话信息，请妥善保管
3. **域名**: 确保导出的是 `https://iam.bangcle.com` 的 Cookie

---

_生成者: Jerry 🦞_

# ONES 系统分析报告

> **生成时间**: 2026-04-12 21:20
> **分析者**: Oliver 🐘

---

## 一、参考数据解析

### 1.1 文件清单
| 文件 | 大小 | 用途 |
|------|------|------|
| ONES_数据字典_3.14.pdf | 3.1MB | 数据库结构参考 |
| 私有部署+-+v3.15.1.pdf | 127MB | 系统功能完整文档 |
| ones-graphQL.sh | 6.3KB | GraphQL API 示例 |
| SQL 使用说明 _ 知识库管理.html | 7.0KB | SQL 操作指南 |
| 产品手册URL.rtf | 505B | 产品手册链接 |

### 1.2 ONES 系统信息

| 项目 | 值 |
|------|-----|
| ONES URL | `https://ones.bangcle.com/` |
| GraphQL API | `https://ones.bangcle.com/project/api/project/team/RZxvwUZ8/items/graphql` |
| 登录 API | `https://ones.bangcle.com/project/api/project/auth/login` |
| 团队 UUID | `RZxvwUZ8` |
| 用户 ID | `REccSDPA` |
| 产品手册 | `https://docs.ones.cn/wiki/#/team/6mRWUuNv/space/66ANjLmW/page/2Zbe2wjw` |
| 帮助手册 | `https://docs.ones.cn/wiki/#/team/6mRWUuNv/space/KmSAAuPb/page/BJxvnL7g` |

### 1.3 GraphQL 可用查询

| 查询类型 | 示例 | 说明 |
|---------|------|------|
| users | `{ users(filter: { name_equal: "xxx" }) { uuid name email } }` | 用户查询 |
| tasks | `{ tasks(filter: { assign: { equal: "xxx" } }) { uuid name } }` | 任务查询 |
| projects | `{ projects(filter: {name_equal: "xxx"}) { uuid name } }` | 项目查询 |
| issueTypes | `{ issueTypes(filter: { uuid_equal: "xxx" }) { uuid name } }` | 问题类型查询 |
| __schema | `{ __schema { queryType { fields { name } } } }` | Schema  introspection |

### 1.4 已知问题类型
- `3Sq3Q7ZK` → "研发任务"

### 1.5 认证方式
- Token 认证: `Ones-Auth-Token` header
- User ID: `Ones-User-Id` header
- 注意: 现有 token 可能已过期

---

## 二、自动化操作清单

| 操作 | 方式 | 可行性 | 说明 |
|------|------|--------|------|
| 登录 | 浏览器自动化 | ✅ | Keychain 凭证 + Playwright |
| 项目列表查询 | GraphQL API | ✅ | 有 API 限制 |
| 任务分配查询 | GraphQL API | ✅ | 有 API 限制 |
| 用户信息查询 | GraphQL API | ✅ | 有 API 限制 |
| 问题类型查询 | GraphQL API | ✅ | 有 API 限制 |
| 项目进度跟踪 | 浏览器 + API | ✅ | 混合方式 |
| 里程碑管理 | 浏览器 | ✅ | 界面操作 |
| 报告导出 | 浏览器 | ✅ | 界面操作 |

---

_分析者: Oliver 🐘_

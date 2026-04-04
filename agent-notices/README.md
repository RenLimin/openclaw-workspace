# 📬 智能体通知系统

**用途**: Jerry 与各智能体间的异步通信

**文件位置**: `workspace/agent-notices/{智能体名}.md`

---

## 🎯 训练前检查清单 (2026-04-04 更新)

### 新增要求

**每次训练开始前，必须执行**：

```markdown
- [ ] 读取 training-memory.md
- [ ] 查看 experiences/{skill}-patterns.json
- [ ] 确认当前版本号
- [ ] 了解之前遇到的问题
- [ ] 基于历史继续训练
```

### 训练记忆本位置

| 智能体 | 记忆本路径 |
|--------|-----------|
| Jerry | `skills/jerry/training-memory.md` |
| Ella | `skills/ella/training-memory.md` |
| Aaron | `skills/aaron/training-memory.md` |
| Oliver | `skills/oliver/training-memory.md` |
| Iris | `skills/iris/training-memory.md` |
| Oscar | `skills/oscar/training-memory.md` |

---

## 📋 通知格式

```markdown
## 📬 待处理通知

**时间**: YYYY-MM-DD HH:MM
**发送方**: Jerry 🦞
**优先级**: 🔴 高 / 🟡 中 / 🟢 低

### 内容
{通知正文}

**状态**: ⏳ 待确认
```

---

## ✅ 状态标记

- ⏳ 待确认
- 🔄 进行中
- ✅ 已完成
- ❌ 已拒绝

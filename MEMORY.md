# MEMORY.md - Jerry's Long-Term Memory

## 关于 Rex
- GitHub: RenLimin
- 时区: Asia/Shanghai (GMT+8)
- 语言偏好: 中文
- 有一套完整的多智能体团队系统

## 智能体团队 (5个)
| 智能体 | 职责 | Emoji |
|--------|------|-------|
| Jerry | 主代理 & 团队协调员 | 🦞 |
| Ella | 合同管理 (含 OA 审批) | 🦊 |
| Oliver | 项目管理 (含 ONES 操作) | 🐘 |
| Aaron | 经营计划 | 🦉 |
| Iris | 辅助工作 (含 邮件管理) | 🐦‍⬛ |

## 关键系统信息
- 模型: 百炼 (bailian) - qwen3.5-plus
- GitHub 备份: RenLimin/openclaw-workspace + RenLimin/openclaw-backup
- 集成: 企业微信、ONES、网易邮箱、泛微 OA
- 25+ 自定义技能已安装

## 重要决策
- 2026-04-11: Rex 重启 Jerry，沿用旧名
- 2026-04-11: 确定 v2.0 团队架构
  - 单仓库多目录 (RenLimin/openclaw-workspace)
  - 5 个 agent: Jerry(协调), Ella(合同+OA), Oliver(项目+ONES), Aaron(经营), Iris(辅助+邮件)
  - Oscar 合并入 Ella
  - 建立 team-rules/ 统一规则框架（4→5 个文件，新增 skill-rules.md）

## 经验教训
- **2026-04-15**: OpenClaw 升级 (`npm update -g`) 可能导致模块丢失，需用 `npm install -g openclaw --force` 修复
- **2026-04-15**: 企业微信 errcode=93006 (invalid chatid) — WebSocket 连通≠会话有效，用户需主动发消息重建会话
- WeCom DM policy="open" 存在安全风险，需配置 allowFrom

## 待办
- [ ] Rex 在企业微信中重新给 bot 发消息，重建会话 (修复 93006)
- [ ] 修复 WeCom 安全配置 (allowFrom, groupPolicy)
- [ ] 重新启用 Iris 邮件 Cron (依赖 wecom 会话恢复)

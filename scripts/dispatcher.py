#!/usr/bin/env python3
"""
Agent Dispatcher Helper
帮助 Jerry 识别消息意图并路由到正确的 Agent

使用方式:
    python3 scripts/dispatcher.py "帮我看看合同审批进度"
    python3 scripts/dispatcher.py --list
"""

import sys
import json

# 路由规则
ROUTING_RULES = [
    {
        "keywords": ["合同", "审批", "OA", "签章", "履约", "报销", "法务"],
        "agent": "ella",
        "emoji": "🦊",
        "name": "Ella"
    },
    {
        "keywords": ["项目", "进度", "ONES", "里程碑", "风险", "任务", "甘特", "排期"],
        "agent": "oliver",
        "emoji": "🐘",
        "name": "Oliver"
    },
    {
        "keywords": ["经营", "数据", "报告", "统计", "KPI", "财务", "仪表盘", "分析"],
        "agent": "aaron",
        "emoji": "🦉",
        "name": "Aaron"
    },
    {
        "keywords": ["邮件", "巡检", "系统", "技术", "研究", "监控", "日志"],
        "agent": "iris",
        "emoji": "🐦‍⬛",
        "name": "Iris"
    }
]


def route_message(message: str) -> dict:
    """根据消息内容路由到对应 Agent"""
    best_match = None
    best_score = 0

    for rule in ROUTING_RULES:
        score = sum(1 for kw in rule["keywords"] if kw.lower() in message.lower())
        if score > best_score:
            best_score = score
            best_match = rule

    if best_match and best_score > 0:
        return {
            "agent": best_match["agent"],
            "name": best_match["name"],
            "emoji": best_match["emoji"],
            "score": best_score,
            "matched_keywords": [
                kw for kw in best_match["keywords"] if kw.lower() in message.lower()
            ]
        }

    return {
        "agent": "main",
        "name": "Jerry",
        "emoji": "🦞",
        "score": 0,
        "matched_keywords": []
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "请提供消息内容", "usage": "python3 dispatcher.py <message>"}, ensure_ascii=False, indent=2))
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    result = route_message(message)
    print(json.dumps(result, ensure_ascii=False, indent=2))

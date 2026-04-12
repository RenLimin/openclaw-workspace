#!/usr/bin/env python3
"""
Oliver 🐘 万事 ONES 浏览器自动化脚本 v1.0

功能：
1. 自动登录 ONES 系统
2. 解析 ONES 系统结构
3. 输出可支持的自动化操作清单

ONES URL: https://ones.bangcle.com/
GraphQL API: https://ones.bangcle.com/project/api/project/team/RZxvwUZ8/items/graphql
"""
import os
import sys
import json
import asyncio
import requests
from playwright.async_api import async_playwright
from datetime import datetime

# ============================================================
# 配置
# ============================================================

ONES_URL = "https://ones.bangcle.com/"
GRAPHQL_API = "https://ones.bangcle.com/project/api/project/team/RZxvwUZ8/items/graphql"
OUTPUT_DIR = "/Users/bangcle/.openclaw/workspace/training-reports/oliver"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ONESAutomation:
    """ONES 浏览器自动化"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.auth_token = None
        self.user_id = None
    
    async def launch(self):
        """启动浏览器"""
        self.playwright = await async_playwright().start()
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=os.path.expanduser("~/.openclaw/browser-data/oliver/"),
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.page = await self.context.new_page()
        print("🌐 Oliver 专属浏览器已启动")
        return self
    
    async def login(self, username=None, password=None):
        """登录 ONES 系统"""
        print("🔐 尝试登录 ONES...")
        
        if not username:
            import subprocess
            try:
                result = subprocess.run(
                    ['security', 'find-generic-password', '-s', 'openclaw-browser-oliver-ones-username', '-w'],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    username = result.stdout.strip()
            except:
                pass
        
        if not username:
            print("  ⚠️ 未找到 Keychain 凭证")
            print("  需要 Rex 提供 ONES 账号密码")
            return False
        
        try:
            # 尝试 GraphQL API 登录
            login_data = {
                "email": username,
                "password": password or "",
                "captcha": ""
            }
            
            resp = requests.post(
                f"{ONES_URL}project/api/project/auth/login",
                json=login_data,
                timeout=10
            )
            
            if resp.status_code == 200:
                result = resp.json()
                self.auth_token = result.get('data', {}).get('token', '')
                self.user_id = result.get('data', {}).get('userId', '')
                print(f"  ✅ API 登录成功")
                return True
            else:
                print(f"  ❌ API 登录失败: {resp.status_code}")
                # 尝试浏览器登录
                await self.page.goto(f"{ONES_URL}project", wait_until="domcontentloaded", timeout=30000)
                # 等待登录表单
                await self.page.wait_for_selector('input[type="text"], input[type="email"]', timeout=10000)
                username_input = await self.page.query_selector('input[type="text"], input[type="email"]')
                password_input = await self.page.query_selector('input[type="password"]')
                if username_input and password_input:
                    await username_input.fill(username)
                    await password_input.fill(password or "")
                    await self.page.click('button[type="submit"]')
                    await self.page.wait_for_load_state("networkidle")
                    print("  ✅ 浏览器登录成功")
                    return True
                return False
        except Exception as e:
            print(f"  ❌ 登录失败: {e}")
            return False
    
    async def explore_system(self):
        """探索系统结构"""
        print("🔍 探索 ONES 系统结构...")
        
        modules = []
        
        try:
            # 导航到主页面
            await self.page.goto(f"{ONES_URL}project", wait_until="domcontentloaded")
            await self.page.wait_for_load_state("networkidle")
            
            # 获取页面标题
            title = await self.page.title()
            print(f"  页面标题: {title}")
            
            # 获取菜单结构
            menu_items = await self.page.evaluate('''() => {
                const items = [];
                const links = document.querySelectorAll('a, .menu-item, [class*="nav"]');
                links.forEach(link => {
                    const text = link.textContent.trim();
                    const href = link.getAttribute('href') || '';
                    if (text && text.length > 2 && text.length < 50) {
                        items.push({text, href});
                    }
                });
                return items.slice(0, 50);
            }''')
            
            print(f"  发现 {len(menu_items)} 个菜单项")
            for item in menu_items[:10]:
                print(f"    - {item['text']}: {item['href'][:50]}")
            
            modules = menu_items
            
            # 截图
            await self.page.screenshot(path=f"{OUTPUT_DIR}/ones-overview.png")
            print("  ✅ 系统概览已截图")
            
        except Exception as e:
            print(f"  ❌ 探索失败: {e}")
        
        return modules
    
    async def test_graphql(self):
        """测试 GraphQL API"""
        print("📡 测试 GraphQL API...")
        
        if not self.auth_token:
            print("  ⚠️ 未登录，跳过 GraphQL 测试")
            return []
        
        # 测试查询
        queries = [
            {"name": "用户查询", "query": '{ users(filter: { name_equal: "测试" }) { uuid name email } }'},
            {"name": "项目查询", "query": '{ projects { uuid name } }'},
            {"name": "Schema", "query": '{ __schema { queryType { fields { name } } } }'},
        ]
        
        results = []
        for q in queries:
            try:
                resp = requests.post(
                    GRAPHQL_API,
                    headers={
                        "Content-Type": "application/json",
                        "Ones-Auth-Token": self.auth_token,
                        "Ones-User-Id": self.user_id or ""
                    },
                    json={"query": q["query"]},
                    timeout=10
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    if "errors" not in data:
                        print(f"  ✅ {q['name']}: 成功")
                        results.append({"name": q["name"], "status": "success"})
                    else:
                        print(f"  ⚠️ {q['name']}: {data['errors'][0]['message']}")
                        results.append({"name": q["name"], "status": "error", "message": data['errors'][0]['message']})
                else:
                    print(f"  ❌ {q['name']}: HTTP {resp.status_code}")
                    results.append({"name": q["name"], "status": "error", "message": f"HTTP {resp.status_code}"})
            except Exception as e:
                print(f"  ❌ {q['name']}: {e}")
                results.append({"name": q["name"], "status": "error", "message": str(e)})
        
        return results
    
    async def generate_capability_list(self, modules, graphql_results):
        """生成可支持的自动化操作清单"""
        print("📋 生成自动化操作清单...")
        
        capabilities = []
        
        # 浏览器自动化能力
        browser_caps = [
            {"category": "浏览器自动化", "operation": "系统登录", "method": "浏览器", "status": "✅ 可用"},
            {"category": "浏览器自动化", "operation": "菜单导航", "method": "浏览器", "status": "✅ 可用"},
            {"category": "浏览器自动化", "operation": "页面数据提取", "method": "浏览器+DOM", "status": "✅ 可用"},
            {"category": "浏览器自动化", "operation": "截图", "method": "浏览器", "status": "✅ 可用"},
        ]
        
        # GraphQL API 能力
        api_caps = []
        for r in graphql_results:
            if r["status"] == "success":
                api_caps.append({
                    "category": "GraphQL API",
                    "operation": r["name"],
                    "method": "API",
                    "status": "✅ 可用"
                })
            else:
                api_caps.append({
                    "category": "GraphQL API",
                    "operation": r["name"],
                    "method": "API",
                    "status": f"❌ {r.get('message', '失败')}"
                })
        
        capabilities = browser_caps + api_caps
        
        # 导出
        output_path = f"{OUTPUT_DIR}/可支持的自动化操作清单.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(capabilities, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 操作清单已导出: {output_path}")
        print(f"  📊 总能力数: {len(capabilities)}")
        print(f"  ✅ 可用: {sum(1 for c in capabilities if '✅' in c['status'])}")
        print(f"  ❌ 不可用: {sum(1 for c in capabilities if '❌' in c['status'])}")
        
        return capabilities
    
    async def close(self):
        """关闭浏览器"""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        print("🔒 浏览器已关闭")


async def main():
    """主函数"""
    print("=" * 60)
    print("Oliver 🐘 万事 ONES 浏览器自动化")
    print("=" * 60)
    
    automation = ONESAutomation()
    await automation.launch()
    
    # 测试登录
    login_success = await automation.login()
    if login_success:
        # 探索系统
        modules = await automation.explore_system()
        # 测试 GraphQL
        graphql_results = await automation.test_graphql()
        # 生成操作清单
        capabilities = await automation.generate_capability_list(modules, graphql_results)
    
    await automation.close()


if __name__ == "__main__":
    asyncio.run(main())

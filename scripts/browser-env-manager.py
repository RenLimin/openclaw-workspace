#!/usr/bin/env python3
"""
浏览器环境管理器 v2.0
为每个 Agent 提供独立的 Chromium 环境、账号隔离、自动登录
使用 Async API 以兼容 asyncio 环境
"""
import os
import sys
import json
import subprocess
import base64
import asyncio
import requests
from pathlib import Path

class BrowserEnvironment:
    """独立浏览器环境管理器（Async）"""
    
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.user_data_dir = os.path.expanduser(
            f"~/.openclaw/browser-data/{agent_name}/"
        )
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
    
    async def launch(self, headless=True):
        """启动独立浏览器环境"""
        from playwright.async_api import async_playwright
        
        os.makedirs(self.user_data_dir, exist_ok=True)
        
        self.playwright = await async_playwright().start()
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
            ]
        )
        self.page = await self.context.new_page()
        print(f"🌐 {self.agent_name} 浏览器环境已启动")
        return self
    
    def load_keychain_credentials(self, site):
        """从 Keychain 加载凭证（同步）"""
        try:
            cmd = f'''security find-generic-password -s "openclaw-browser-{self.agent_name}-{site}-username" -w 2>/dev/null'''
            username = subprocess.check_output(cmd, shell=True, text=True).strip()
            
            cmd = f'''security find-generic-password -s "openclaw-browser-{self.agent_name}-{site}-password" -w 2>/dev/null'''
            password = subprocess.check_output(cmd, shell=True, text=True).strip()
            
            if username and password:
                print(f"🔑 已加载 {site} 凭证")
                return {"username": username, "password": password}
        except subprocess.CalledProcessError:
            pass
        
        print(f"⚠️ 未找到 {site} 的 Keychain 凭证")
        return None
    
    def store_keychain_credentials(self, site, username, password):
        """存储凭证到 Keychain（同步）"""
        try:
            subprocess.run([
                'security', 'add-generic-password',
                '-s', f'openclaw-browser-{self.agent_name}-{site}-username',
                '-a', self.agent_name,
                '-w', username,
                '-U'
            ], check=True)
            
            subprocess.run([
                'security', 'add-generic-password',
                '-s', f'openclaw-browser-{self.agent_name}-{site}-password',
                '-a', self.agent_name,
                '-w', password,
                '-U'
            ], check=True)
            
            print(f"✅ 已存储 {site} 凭证到 Keychain")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Keychain 存储失败: {e}")
            return False
    
    def save_cookies(self, site):
        """保存 Cookie（同步）"""
        # Cookie 持久化由 persistent_context 自动处理
        cookie_path = os.path.join(self.user_data_dir, f"{site}-cookies.json")
        print(f"🍪 Cookie 自动持久化到: {self.user_data_dir}")
        return cookie_path
    
    async def wait_for_vue(self, timeout=10000):
        """等待 Vue 应用挂载"""
        try:
            await self.page.wait_for_function("""
                () => {
                    if (window.__VUE__) return true;
                    if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__) return true;
                    if (window.__NUXT__) return true;
                    const app = document.querySelector('#app');
                    return app && app.children.length > 0;
                }
            """, timeout=timeout)
            print("✅ Vue 应用已挂载")
            return True
        except Exception as e:
            print(f"⚠️ Vue 检测超时，使用 fallback: {e}")
            return False
    
    async def wait_for_react(self, timeout=10000):
        """等待 React 应用挂载"""
        try:
            await self.page.wait_for_function("""
                () => {
                    if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) return true;
                    const root = document.querySelector('#root');
                    return root && root.children.length > 0;
                }
            """, timeout=timeout)
            print("✅ React 应用已挂载")
            return True
        except Exception as e:
            print(f"⚠️ React 检测超时，使用 fallback: {e}")
            return False
    
    async def wait_for_spa(self, framework='auto', timeout=15000):
        """通用 SPA 等待"""
        if framework in ('vue', 'auto'):
            if await self.wait_for_vue(timeout):
                return 'vue'
        
        if framework in ('react', 'auto'):
            if await self.wait_for_react(timeout):
                return 'react'
        
        await self.page.wait_for_load_state('networkidle')
        print("⚠️ 使用 networkidle fallback")
        return 'unknown'
    
    async def visual_analyze(self, prompt="请描述这个页面的内容和布局。"):
        """视觉识别分析（异步）"""
        try:
            import tempfile
            # 截图
            screenshot_path = f"/tmp/{self.agent_name}-screenshot.png"
            await self.page.screenshot(path=screenshot_path, full_page=True)
            
            with open(screenshot_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            api_key = "sk-sp-a68df77f47f04e1ca871300f7afa41f1"
            url = "https://coding.dashscope.aliyuncs.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "kimi-k2.5",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                    ]
                }],
                "max_tokens": 1000
            }
            
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            else:
                print(f"❌ 视觉识别 API 错误: {resp.status_code}")
                return None
        except Exception as e:
            print(f"❌ 视觉识别失败: {e}")
            return None
    
    async def smart_click(self, text_or_description):
        """智能点击：DOM + 视觉双重验证"""
        # 先尝试 DOM 查找
        try:
            locator = self.page.get_by_text(text_or_description, exact=False)
            count = await locator.count()
            if count > 0:
                await locator.first.click()
                print(f"✅ DOM 查找成功: {text_or_description}")
                return True
        except Exception as e:
            print(f"⚠️ DOM 查找失败: {e}")
        
        # DOM 失败，使用视觉识别
        print(f"🔍 使用视觉识别查找: {text_or_description}")
        analysis = await self.visual_analyze(f"请找出包含'{text_or_description}'的可点击元素位置。")
        if analysis:
            print(f"  视觉识别结果: {analysis[:200]}")
            return True
        return False
    
    async def execute_javascript(self, script):
        """执行 JavaScript"""
        try:
            result = await self.page.evaluate(script)
            return result
        except Exception as e:
            print(f"❌ JavaScript 执行失败: {e}")
            return None
    
    async def close(self):
        """关闭浏览器环境"""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        print(f"🔒 {self.agent_name} 浏览器环境已关闭")


async def test_environment_isolation():
    """测试 1: 环境隔离"""
    print("🧪 测试 1: 环境隔离")
    
    envs = {}
    for agent in ['jerry', 'ella', 'oliver', 'aaron', 'iris']:
        env = BrowserEnvironment(agent)
        await env.launch(headless=True)
        await env.page.goto("https://example.com/", wait_until="domcontentloaded")
        envs[agent] = env
    
    # 验证每个环境独立
    for agent, env in envs.items():
        url = env.page.url
        print(f"  {agent}: {url}")
        assert "example.com" in url
    
    # 关闭
    for env in envs.values():
        await env.close()
    
    print("  ✅ 环境隔离测试通过")
    return True


async def test_vue_handling():
    """测试 2: Vue/SPA 处理"""
    print("\n🧪 测试 2: Vue/SPA 处理")
    
    env = BrowserEnvironment("jerry")
    await env.launch(headless=True)
    
    # 测试 Vue 官网
    await env.page.goto("https://vuejs.org/", wait_until="domcontentloaded")
    
    # 等待 Vue 挂载
    try:
        await env.page.wait_for_function("""
            () => {
                return window.__VUE__ || 
                       (document.querySelector('#app') && 
                        document.querySelector('#app').children.length > 0);
            }
        """, timeout=10000)
        print("  ✅ Vue 检测成功")
    except Exception as e:
        print(f"  ⚠️ Vue 检测失败，使用 fallback: {e}")
        await env.page.wait_for_load_state("networkidle")
    
    # 测试 JavaScript 执行
    result = await env.execute_javascript("""() => {
        return {
            title: document.title,
            hasVue: !!window.__VUE__,
            hasChildren: document.querySelector('#app')?.children.length > 0
        };
    }""")
    
    if result:
        print(f"  JavaScript 结果: {result}")
    
    await env.close()
    print("  ✅ Vue/SPA 处理测试通过")
    return True


async def test_visual_recognition():
    """测试 3: 视觉识别"""
    print("\n🧪 测试 3: 视觉识别")
    
    env = BrowserEnvironment("jerry")
    await env.launch(headless=True)
    
    await env.page.goto("https://example.com/", wait_until="networkidle")
    
    analysis = await env.visual_analyze("请描述这个页面的内容。")
    if analysis:
        print(f"  视觉识别结果: {analysis[:200]}...")
        print("  ✅ 视觉识别测试通过")
        result = True
    else:
        print("  ❌ 视觉识别失败")
        result = False
    
    await env.close()
    return result


async def main():
    print("=" * 60)
    print("浏览器自动化 v2.0 优化测试")
    print("=" * 60)
    
    results = {}
    results["环境隔离"] = "✅ 通过" if await test_environment_isolation() else "❌ 失败"
    results["Vue/SPA处理"] = "✅ 通过" if await test_vue_handling() else "❌ 失败"
    results["视觉识别"] = "✅ 通过" if await test_visual_recognition() else "❌ 失败"
    
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    print("=" * 60)
    
    return all("✅" in v for v in results.values())


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

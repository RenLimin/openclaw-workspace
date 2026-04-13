#!/usr/bin/env python3
"""
获取 API 基础路径并正确调用 jumpSystem
"""

import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        out = '/Users/bangcle/.openclaw/workspace/training-reports/ella/'
        
        print("=" * 60)
        print("获取 API 基础路径并调用 jumpSystem")
        print("=" * 60)
        
        # Login
        await page.goto('https://iam.bangcle.com/', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(3)
        
        if 'home' not in page.url and 'index' not in page.url:
            inputs = await page.query_selector_all('input')
            text_inputs = [i for i in inputs 
                          if await i.get_attribute('type') in ['text','password','email','tel'] 
                          and await i.is_visible()]
            if len(text_inputs) >= 2:
                await text_inputs[0].fill('limin.ren')
                await text_inputs[1].fill('June-123')
                btn = page.get_by_role("button", name="登录")
                if await btn.is_visible():
                    await btn.click()
                else:
                    await text_inputs[1].press('Enter')
                await asyncio.sleep(10)
        
        await page.goto('https://iam.bangcle.com/#/home/index', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(8)
        
        # Get token and API base URL
        print("\nStep 1: 获取 Token 和 API 基础路径...")
        
        info = await page.evaluate("""() => {
            const state = JSON.parse(localStorage.getItem('GlobalState') || '{}');
            const token = state.token || '';
            
            // Try to find API base URL from the page's JS
            // Look for axios instance configuration
            const scripts = document.querySelectorAll('script[src]');
            let baseUrl = '';
            
            return {
                token: token.substring(0, 50),
                hasToken: !!token,
                location: window.location.origin
            };
        }""")
        print(f"  Token: {info['token']}...")
        print(f"  Origin: {info['location']}")
        
        # Step 2: Call jumpSystem with proper Authorization header
        print("\nStep 2: 调用 jumpSystem (带 Authorization)...")
        
        result = await page.evaluate("""async () => {
            const state = JSON.parse(localStorage.getItem('GlobalState') || '{}');
            const token = state.token || '';
            
            try {
                const resp = await fetch('/api/application/apps/jumpSystem?appid=9', {
                    method: 'GET',
                    headers: {
                        'Authorization': 'Bearer ' + token,
                        'noLoading': 'true'
                    }
                });
                const text = await resp.text();
                return {status: resp.status, text: text.substring(0, 500)};
            } catch(e) {
                return {error: e.message};
            }
        }""")
        print(f"  结果: {result}")
        
        # Step 3: Also try to get app list with proper auth
        print("\nStep 3: 获取应用列表 (带 Authorization)...")
        
        apps_result = await page.evaluate("""async () => {
            const state = JSON.parse(localStorage.getItem('GlobalState') || '{}');
            const token = state.token || '';
            
            try {
                const resp = await fetch('/api/application/apps/getPermissionApps', {
                    method: 'POST',
                    headers: {
                        'Authorization': 'Bearer ' + token,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({userId: state.userInfo?.userid || '1313'})
                });
                const data = await resp.json();
                return data;
            } catch(e) {
                return {error: e.message};
            }
        }""")
        
        if 'error' not in apps_result:
            app_list = apps_result.get('data', [])
            print(f"  应用数量: {len(app_list)}")
            for app in app_list:
                print(f"    - {app.get('systemname')}: id={app.get('id')}, domain={app.get('domain')}, link={app.get('systemlink')}")
        else:
            print(f"  ❌ {apps_result}")
        
        await browser.close()

asyncio.run(main())

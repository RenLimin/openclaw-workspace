#!/usr/bin/env python3
"""
获取应用列表并调用 jumpSystem API - 调试版
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
        print("获取应用列表并调用 jumpSystem API")
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
        print(f"URL: {page.url}")
        
        # Step 1: Try different API endpoints
        print("\nStep 1: 尝试不同 API 端点...")
        
        endpoints = [
            ('POST', '/apps/getPermissionApps', {'userId': '1313'}),
            ('POST', '/apps/getApps', {}),
            ('GET', '/apps/jumpSystem?appid=1', None),
        ]
        
        for method, path, body in endpoints:
            try:
                if method == 'POST':
                    result = await page.evaluate(f"""async () => {{
                        try {{
                            const resp = await fetch('{path}', {{
                                method: 'POST',
                                headers: {{'Content-Type': 'application/json'}},
                                body: JSON.stringify({json.dumps(body)})
                            }});
                            const text = await resp.text();
                            return {{status: resp.status, text: text.substring(0, 300)}};
                        }} catch(e) {{
                            return {{error: e.message}};
                        }}
                    }}""")
                else:
                    result = await page.evaluate(f"""async () => {{
                        try {{
                            const resp = await fetch('{path}', {{
                                method: 'GET'
                            }});
                            const text = await resp.text();
                            return {{status: resp.status, text: text.substring(0, 300)}};
                        }} catch(e) {{
                            return {{error: e.message}};
                        }}
                    }}""")
                print(f"  {method} {path}: {result}")
            except Exception as e:
                print(f"  {method} {path}: ❌ {e}")
        
        # Step 2: Get the app list data from the Vue component
        print("\nStep 2: 从 Vue 组件获取应用数据...")
        
        # Wait for the app list to load
        await asyncio.sleep(3)
        
        # Try to get app data from page state
        app_data = await page.evaluate("""() => {
            // Check if there's any global state with app data
            const keys = Object.keys(window).filter(k => k.includes('app') || k.includes('App'));
            return {keys: keys.slice(0, 10)};
        }""")
        print(f"  Window keys: {app_data}")
        
        # Step 3: Intercept network requests when loading page
        print("\nStep 3: 拦截页面加载时的 API 请求...")
        
        # Reload and intercept
        captured = []
        
        async def on_response(response):
            if 'apps' in response.url.lower():
                try:
                    data = await response.json()
                    captured.append({
                        'url': response.url,
                        'status': response.status,
                        'data': str(data)[:500]
                    })
                    print(f"  🎯 {response.url}: {str(data)[:200]}")
                except:
                    pass
        
        page.on("response", on_response)
        
        # Reload to trigger API calls
        await page.reload(wait_until='networkidle', timeout=30000)
        await asyncio.sleep(5)
        
        print(f"\n  捕获到 {len(captured)} 个 API 响应")
        
        # Step 4: Try to manually find OA app ID and call jumpSystem
        print("\nStep 4: 手动获取 OA 跳转 URL...")
        
        # From the NewApp component, the app list is loaded via ht (getApps) or mt (getBacklog)
        # Let's try to call the API directly
        try:
            get_apps_result = await page.evaluate("""async () => {
                try {
                    const resp = await fetch('/apps/getPermissionApps', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({userId: '1313'})
                    });
                    const text = await resp.text();
                    return {status: resp.status, text: text.substring(0, 500)};
                } catch(e) {
                    return {error: e.message};
                }
            }""")
            print(f"  getPermissionApps: {get_apps_result}")
        except Exception as e:
            print(f"  ❌ {e}")
        
        await browser.close()

asyncio.run(main())

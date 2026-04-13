#!/usr/bin/env python3
"""
获取 apps JS 文件，找到 OA 跳转 URL
"""

import asyncio
import json
import re
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        out = '/Users/bangcle/.openclaw/workspace/training-reports/ella/'
        
        print("=" * 60)
        print("获取 apps JS，找到 OA 跳转 URL")
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
        
        print("\nStep 1: 获取 apps JS 文件...")
        apps_js = 'https://iam.bangcle.com/assets/js/apps-e1e0da33.js'
        content = await page.evaluate(f"""async () => {{
            try {{
                const resp = await fetch('{apps_js}');
                return await resp.text();
            }} catch(e) {{
                return 'ERROR: ' + e.message;
            }}
        }}""")
        
        if not content.startswith('ERROR:'):
            with open(f'{out}apps-e1e0da33.js', 'w') as f:
                f.write(content)
            print(f"  ✅ 已保存 apps-e1e0da33.js ({len(content)} bytes)")
            
            # Find all URLs
            urls = re.findall(r'https?://[^\s"\')\]}]+', content)
            print(f"\n  找到 {len(urls)} 个 URL:")
            for u in set(urls):
                print(f"    {u}")
            
            # Find the H function
            print("\n  查找 H 函数 (getAppUrl 或类似)...")
            # Look for export patterns
            exports = re.findall(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|\w+)\s*=>', content)
            print(f"  函数: {exports}")
        else:
            print(f"  ❌ {content}")
        
        # Step 2: Use JS to call the app URL API
        print("\nStep 2: 通过 JS 获取 OA 的跳转 URL...")
        
        # Find OA app ID from the page
        app_info = await page.evaluate("""() => {
            // Find the app list data
            const state = JSON.parse(localStorage.getItem('GlobalState') || '{}');
            
            // Check if there's app data in the Vue app
            const app = document.querySelector('#app');
            if (app && app.__vue_app__) {
                // Try to access Vue 3 instance
                return {hasVueApp: true};
            }
            
            return {hasVueApp: false};
        }""")
        print(f"  Vue 应用: {app_info}")
        
        # Step 3: Try to call the app API directly
        print("\nStep 3: 尝试调用应用 API...")
        
        # Get the token
        global_state = await page.evaluate("() => localStorage.getItem('GlobalState')")
        state = json.loads(global_state)
        token = state.get('token', '')
        user_id = state.get('userInfo', {}).get('userid', '')
        
        print(f"  Token: {token[:30]}...")
        print(f"  User ID: {user_id}")
        
        # Try to find the API endpoint for app URLs
        # From NewApp, H(e.id) is called - let's find what H is
        # Looking at imports: import {a as ht, b as mt, l as H} from "./apps-e1e0da33.js"
        # So H is the 3rd export (l)
        
        # Try common API patterns
        api_patterns = [
            '/api/system/app/url',
            '/api/app/redirect',
            '/api/app/getUrl',
            '/api/app/getAppUrl',
            '/api/portal/app/url',
            '/api/app/entry',
            '/system/app/getUrl',
            '/api/app/jump',
        ]
        
        for api in api_patterns:
            url = f'https://iam.bangcle.com{api}'
            try:
                response = await page.evaluate(f"""async () => {{
                    try {{
                        const resp = await fetch('{url}', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                                'Authorization': 'Bearer {token}'
                            }},
                            body: JSON.stringify({{id: 'oa', appId: 'oa', systemkey: 'oa'}})
                        }});
                        const text = await resp.text();
                        return {{status: resp.status, body: text.substring(0, 200)}};
                    }} catch(e) {{
                        return {{error: e.message}};
                    }}
                }}""")
                if 'error' not in str(response):
                    print(f"  {api}: {response}")
            except:
                pass
        
        # Step 4: Intercept app click network requests
        print("\nStep 4: 拦截应用点击的网络请求...")
        print("  请手动点击 OA 卡片...")
        
        captured_urls = []
        
        async def on_request(request):
            if any(kw in request.url.lower() for kw in ['app', 'entry', 'redirect', 'jump', 'url', 'sso']):
                captured_urls.append({
                    'url': request.url,
                    'method': request.method,
                    'post_data': request.post_data[:200] if request.post_data else None
                })
                print(f"  🎯 {request.method} {request.url[:100]}")
                if request.post_data:
                    print(f"     数据: {request.post_data[:200]}")
        
        page.on("request", on_request)
        
        # Wait for manual click
        for _ in range(30):
            await asyncio.sleep(5)
            url = page.url
            if 'oa.bangcle.com' in url and 'iam' not in url:
                print(f"\n  ✅ 检测到跳转! {url}")
                cookies = await context.cookies()
                with open(out + 'oa-working-cookies.json', 'w') as f:
                    json.dump(cookies, f, indent=2)
                await context.storage_state(path=out + 'oa-working-state.json')
                await page.screenshot(path=out + 'oa-success.png', full_page=True)
                print(f"  🍪 Cookie 已保存")
                break
        
        print(f"\n  捕获到的请求:")
        for req in captured_urls:
            print(f"    {req['method']} {req['url'][:80]}")
        
        await browser.close()

asyncio.run(main())

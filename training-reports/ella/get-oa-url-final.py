#!/usr/bin/env python3
"""
调用 jumpSystem API 获取 OA 跳转 URL
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
        print("调用 jumpSystem API 获取 OA 跳转 URL")
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
        
        print("\nStep 1: 调用 jumpSystem API (OA ID=9)...")
        
        # Try different URL patterns for jumpSystem
        urls_to_try = [
            '/api/application/apps/jumpSystem?appid=9',
            '/api/application/apps/jumpSystem',
        ]
        
        for url in urls_to_try:
            print(f"\n  尝试: {url}")
            try:
                if '?' in url:
                    result = await page.evaluate(f"""async () => {{
                        try {{
                            const resp = await fetch('{url}', {{
                                method: 'GET',
                                headers: {{'noLoading': 'true'}}
                            }});
                            const text = await resp.text();
                            return {{status: resp.status, text: text.substring(0, 500)}};
                        }} catch(e) {{
                            return {{error: e.message}};
                        }}
                    }}""")
                else:
                    result = await page.evaluate(f"""async () => {{
                        try {{
                            const resp = await fetch('{url}', {{
                                method: 'POST',
                                headers: {{'Content-Type': 'application/json'}},
                                body: JSON.stringify({{appid: 9}})
                            }});
                            const text = await resp.text();
                            return {{status: resp.status, text: text.substring(0, 500)}};
                        }} catch(e) {{
                            return {{error: e.message}};
                        }}
                    }}""")
                print(f"  结果: {result}")
            except Exception as e:
                print(f"  ❌ {e}")
        
        # Step 2: Try the assets/login endpoint (for password-based login, appid=9)
        print("\nStep 2: 尝试 assets/login API (appid=9)...")
        
        login_result = await page.evaluate("""async () => {
            try {
                const resp = await fetch('/assets/login?appid=9', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                const text = await resp.text();
                return {status: resp.status, text: text.substring(0, 500)};
            } catch(e) {
                return {error: e.message};
            }
        }""")
        print(f"  结果: {login_result}")
        
        # Step 3: Intercept click on OA card
        print("\nStep 3: 拦截 OA 卡片点击的所有请求...")
        print("  请手动点击 OA 卡片...")
        
        captured = []
        async def on_request(request):
            if any(kw in request.url.lower() for kw in ['app', 'jump', 'login', 'sso', 'oa', 'asset']):
                captured.append({
                    'url': request.url,
                    'method': request.method,
                    'post_data': request.post_data[:200] if request.post_data else None
                })
                print(f"  🎯 {request.method} {request.url[:100]}")
        
        page.on("request", on_request)
        
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
        for req in captured:
            print(f"    {req['method']} {req['url'][:80]}")
            if req['post_data']:
                print(f"      数据: {req['post_data']}")
        
        await browser.close()

asyncio.run(main())

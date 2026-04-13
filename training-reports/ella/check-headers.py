#!/usr/bin/env python3
"""
检查成功 API 请求的 headers
"""

import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        print("=" * 60)
        print("检查成功 API 请求的 headers")
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
        
        # Intercept successful requests
        print("\n拦截 API 请求...")
        captured = []
        
        async def on_request(request):
            if 'getPermissionApps' in request.url or 'getBacklog' in request.url:
                captured.append({
                    'url': request.url,
                    'method': request.method,
                    'headers': request.headers,
                    'post_data': request.post_data
                })
                print(f"\n  🎯 {request.method} {request.url}")
                print(f"  Headers:")
                for k, v in request.headers.items():
                    if k.lower() not in ['cookie', 'host', 'connection', 'accept', 'accept-encoding', 'accept-language', 'sec-fetch', 'sec-ch', 'origin', 'referer', 'user-agent']:
                        print(f"    {k}: {v}")
                if request.post_data:
                    print(f"  Data: {request.post_data}")
        
        page.on("request", on_request)
        
        # Reload to trigger requests
        await page.reload(wait_until='networkidle', timeout=30000)
        await asyncio.sleep(5)
        
        print(f"\n\n捕获到 {len(captured)} 个请求")
        
        # Try to call the API with the same headers
        if captured:
            print("\n使用相同的 headers 调用 jumpSystem...")
            req = captured[0]
            
            # Build headers dict
            headers = {k: v for k, v in req['headers'].items() 
                      if k.lower() not in ['host', 'connection', 'content-length', 'cookie']}
            
            # Call jumpSystem
            result = await page.evaluate(f"""async () => {{
                try {{
                    const resp = await fetch('/api/application/apps/jumpSystem?appid=9', {{
                        method: 'GET',
                        headers: {json.dumps(headers)}
                    }});
                    const text = await resp.text();
                    return {{status: resp.status, text: text.substring(0, 500)}};
                }} catch(e) {{
                    return {{error: e.message}};
                }}
            }}""")
            print(f"  结果: {result}")
        
        await browser.close()

asyncio.run(main())

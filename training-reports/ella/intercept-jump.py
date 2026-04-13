#!/usr/bin/env python3
"""
拦截 /apps/jumpSystem API 调用，获取 OA 跳转 URL
"""

import asyncio
import json
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
        print("拦截 /apps/jumpSystem API")
        print("=" * 60)
        
        # Setup request interception
        jump_url = None
        jump_response_data = None
        
        async def on_response(response):
            nonlocal jump_url, jump_response_data
            if 'jumpSystem' in response.url:
                try:
                    data = await response.json()
                    jump_url = response.url
                    jump_response_data = data
                    print(f"\n  🎯 捕获到 jumpSystem 响应!")
                    print(f"  请求 URL: {response.url}")
                    print(f"  响应: {json.dumps(data, ensure_ascii=False)}")
                except:
                    pass
        
        page.on("response", on_response)
        
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
        
        print("\n  已设置拦截器，请手动点击 OA 卡片...")
        print("  我会捕获 /apps/jumpSystem 的响应")
        
        # Wait for manual click
        for _ in range(30):
            await asyncio.sleep(5)
            if jump_response_data:
                print(f"\n  ✅ 已捕获跳转 URL!")
                
                # Get the redirect URL from response
                redirect_url = jump_response_data.get('data', '')
                if isinstance(redirect_url, dict):
                    redirect_url = redirect_url.get('url', '') or redirect_url.get('redirectUrl', '')
                
                print(f"  跳转 URL: {redirect_url}")
                
                if redirect_url:
                    # Try to directly access the redirect URL
                    print(f"\n  尝试直接访问: {redirect_url}")
                    await page.goto(redirect_url, wait_until='networkidle', timeout=30000)
                    await asyncio.sleep(10)
                    print(f"  结果 URL: {page.url}")
                    
                    if 'oa.bangcle.com' in page.url:
                        print("  ✅ 成功进入 OA!")
                        cookies = await context.cookies()
                        with open(out + 'oa-working-cookies.json', 'w') as f:
                            json.dump(cookies, f, indent=2)
                        await context.storage_state(path=out + 'oa-working-state.json')
                        await page.screenshot(path=out + 'oa-success.png', full_page=True)
                        print(f"  🍪 Cookie 已保存")
                    else:
                        print(f"  ⚠️ 未进入 OA，URL: {page.url}")
                break
            
            url = page.url
            if 'oa.bangcle.com' in url and 'iam' not in url:
                print(f"\n  ✅ 直接检测到跳转! {url}")
                cookies = await context.cookies()
                with open(out + 'oa-working-cookies.json', 'w') as f:
                    json.dump(cookies, f, indent=2)
                await context.storage_state(path=out + 'oa-working-state.json')
                await page.screenshot(path=out + 'oa-success.png', full_page=True)
                break
        
        if not jump_response_data:
            print("\n  未捕获到 jumpSystem 请求")
            print("  浏览器保持打开，请手动点击...")
            for _ in range(12):
                await asyncio.sleep(5)
                url = page.url
                if 'oa.bangcle.com' in url and 'iam' not in url:
                    print(f"  ✅ 检测到跳转! {url}")
                    cookies = await context.cookies()
                    with open(out + 'oa-working-cookies.json', 'w') as f:
                        json.dump(cookies, f, indent=2)
                    await context.storage_state(path=out + 'oa-working-state.json')
                    await page.screenshot(path=out + 'oa-success.png', full_page=True)
                    break
        
        await browser.close()

asyncio.run(main())

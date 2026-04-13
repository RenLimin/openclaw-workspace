#!/usr/bin/env python3
"""
使用 jumpSystem 返回的 URL 访问 OA
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
        print("使用 jumpSystem URL 访问 OA")
        print("=" * 60)
        
        # Login to IAM
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
        
        # Get jump URL
        print("\nStep 1: 获取 OA 跳转 URL...")
        jump_result = await page.evaluate("""async () => {
            const state = JSON.parse(localStorage.getItem('GlobalState') || '{}');
            const token = state.token;
            
            try {
                const resp = await fetch('/api/application/apps/jumpSystem?appid=9', {
                    method: 'GET',
                    headers: {
                        'x-access-token': token,
                        'noLoading': 'true'
                    }
                });
                const data = await resp.json();
                return data;
            } catch(e) {
                return {error: e.message};
            }
        }""")
        print(f"  响应: {jump_result}")
        
        oa_url = jump_result.get('data', '')
        if not oa_url:
            print("  ❌ 未获取到 URL")
            await browser.close()
            return
        
        print(f"\n  OA URL: {oa_url}")
        
        # Step 2: Navigate to OA URL
        print("\nStep 2: 访问 OA 跳转 URL...")
        await page.goto(oa_url, wait_until='networkidle', timeout=60000)
        await asyncio.sleep(15)
        
        print(f"  结果 URL: {page.url}")
        
        if 'oa.bangcle.com' in page.url and 'login' not in page.url.lower() and 'iam' not in page.url.lower():
            print("\n" + "=" * 60)
            print("✅ 成功进入 OA!")
            print("=" * 60)
            
            # Save cookies
            cookies = await context.cookies()
            with open(out + 'oa-working-cookies.json', 'w') as f:
                json.dump(cookies, f, indent=2)
            print(f"  🍪 Cookie 已保存: {len(cookies)} 个")
            
            # Save storage state
            await context.storage_state(path=out + 'oa-working-state.json')
            print(f"  💾 Storage state 已保存")
            
            # Screenshot
            await page.screenshot(path=out + 'oa-success.png', full_page=True)
            print(f"  📸 截图已保存")
            
            # Show cookies
            for c in cookies:
                if 'bangcle' in c.get('domain', ''):
                    print(f"    {c['name']}: domain={c.get('domain')}, httpOnly={c.get('httpOnly', False)}")
        else:
            print(f"\n⚠️ 未进入 OA")
            await page.screenshot(path=out + 'oa-jump-result.png', full_page=True)
            print(f"  📸 截图已保存")
        
        await browser.close()

asyncio.run(main())

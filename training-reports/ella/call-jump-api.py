#!/usr/bin/env python3
"""
直接调用 /apps/jumpSystem API 获取 OA URL - 修复版
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
        print("通过页面 JS 调用 jumpSystem API")
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
        
        # Step 1: Get app list via page JS
        print("\nStep 1: 获取应用列表...")
        apps = await page.evaluate("""async () => {
            try {
                const state = JSON.parse(localStorage.getItem('GlobalState'));
                const token = state.token;
                const userId = state.userInfo.userid;
                
                const resp = await fetch('/apps/getPermissionApps', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'noLoading': 'true'
                    },
                    body: JSON.stringify({userId: userId})
                });
                const data = await resp.json();
                return data;
            } catch(e) {
                return {error: e.message};
            }
        }""")
        
        if 'error' in apps:
            print(f"  ❌ {apps['error']}")
        else:
            app_list = apps.get('data', [])
            print(f"  应用数量: {len(app_list)}")
            for app in app_list:
                print(f"    - {app.get('systemname')}: id={app.get('id')}, key={app.get('systemkey')}, link={app.get('systemlink')}")
                
                if 'OA' in app.get('systemname', '') or '协同' in app.get('systemname', ''):
                    oa_id = app.get('id')
                    print(f"\n  ✅ 找到 OA! ID={oa_id}")
                    
                    # Step 2: Call jumpSystem
                    print(f"\nStep 2: 调用 jumpSystem API...")
                    jump_resp = await page.evaluate(f"""async () => {{
                        try {{
                            const resp = await fetch('/apps/jumpSystem?appid={oa_id}', {{
                                method: 'GET',
                                headers: {{
                                    'noLoading': 'true'
                                }}
                            }});
                            const data = await resp.json();
                            return {{
                                status: resp.status,
                                url: resp.url,
                                data: data,
                                redirectUrl: resp.redirected ? resp.url : null
                            }};
                        }} catch(e) {{
                            return {{error: e.message}};
                        }}
                    }}""")
                    
                    print(f"  响应: {json.dumps(jump_resp, ensure_ascii=False)[:500]}")
                    
                    # Get the redirect URL
                    redirect_url = None
                    if isinstance(jump_resp.get('data'), dict):
                        redirect_url = jump_resp['data'].get('url') or jump_resp['data'].get('redirectUrl') or jump_resp['data'].get('data')
                    elif isinstance(jump_resp.get('data'), str):
                        redirect_url = jump_resp['data']
                    
                    if redirect_url:
                        print(f"\n  跳转 URL: {redirect_url}")
                        
                        # Try to navigate to the URL
                        print(f"\nStep 3: 尝试访问跳转 URL...")
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
                            print(f"  🍪 Cookie 已保存: {len(cookies)} 个")
                        else:
                            print(f"  ⚠️ 未进入 OA")
                            await page.screenshot(path=out + 'oa-jump-url-result.png', full_page=True)
                    else:
                        print(f"  ❌ 未获取到跳转 URL")
                    break
        
        await browser.close()

asyncio.run(main())

#!/usr/bin/env python3
"""
OA 登录 - 使用 IAM Token + 分析 JS 源码
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
        print("使用 IAM Token + 分析 JS 源码")
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
        
        # Get IAM token
        print("\nStep 1: 获取 IAM Token...")
        global_state = await page.evaluate("() => localStorage.getItem('GlobalState')")
        if global_state:
            state = json.loads(global_state)
            token = state.get('token', '')
            print(f"  Token: {token[:50]}...")
        else:
            print("  ❌ 未找到 token")
            await browser.close()
            return
        
        # Step 2: Analyze JS files for OA URL patterns
        print("\nStep 2: 分析 JS 文件中的 SSO 和 OA 跳转逻辑...")
        
        # Focus on key JS files
        key_files = [
            'https://iam.bangcle.com/assets/js/index-be1d885b.js',  # mentions sso
            'https://iam.bangcle.com/assets/js/NewApp-8cc580f5.js',  # app cards
            'https://iam.bangcle.com/assets/js/user-50fe7d17.js',
        ]
        
        for url in key_files:
            print(f"\n  分析: {url.split('/')[-1]}")
            try:
                response = await page.evaluate(f"""async () => {{
                    try {{
                        const resp = await fetch('{url}');
                        return await resp.text();
                    }} catch(e) {{
                        return 'ERROR: ' + e.message;
                    }}
                }}""")
                
                if response.startswith('ERROR:'):
                    print(f"    ❌ {response}")
                    continue
                
                print(f"    大小: {len(response)} bytes")
                
                # Search for URL patterns
                url_patterns = re.findall(r'https?://[^\s"\']+', response)
                oa_urls = [u for u in url_patterns if 'oa' in u.lower() or 'bangcle.com' in u.lower()]
                if oa_urls:
                    print(f"    URL 模式 ({len(oa_urls)} 个):")
                    for u in set(oa_urls)[:10]:
                        print(f"      {u}")
                
                # Search for SSO-related patterns
                sso_patterns = re.findall(r'(?:sso|SSO|ssoUrl|sso_url|ssoToken|token)[=:\"\']([^\"\']{5,})', response)
                if sso_patterns:
                    print(f"    SSO 模式 ({len(sso_patterns)} 个):")
                    for s in set(sso_patterns)[:5]:
                        print(f"      {s[:80]}")
                
                # Search for app entry/click handlers
                click_patterns = re.findall(r'(?:goTo|navigate|redirect|openApp|appUrl|appLink|entryUrl|targetUrl)[=:\"\']([^\"\']{5,})', response)
                if click_patterns:
                    print(f"    跳转模式 ({len(click_patterns)} 个):")
                    for c in set(click_patterns)[:5]:
                        print(f"      {c[:80]}")
                
                # Save the JS content for further analysis
                filename = url.split('/')[-1]
                with open(f'{out}{filename}', 'w') as f:
                    f.write(response)
                print(f"    💾 已保存到 {filename}")
                
            except Exception as e:
                print(f"    ❌ {e}")
        
        # Step 3: Try SSO with token
        print("\nStep 3: 尝试 SSO URL 携带 Token...")
        
        sso_tests = [
            f'https://oa.bangcle.com/api/sso/login?token={token[:50]}',
            f'https://oa.bangcle.com/login/VerifyLoginWeaversso.jsp?message=315&appid=ecology&service=https://oa.bangcle.com/wui/index.html&token={token[:50]}',
        ]
        
        for url in sso_tests[:1]:
            print(f"  尝试: {url[:80]}...")
            try:
                response = await page.evaluate(f"""async () => {{
                    try {{
                        const resp = await fetch('{url}', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            credentials: 'include',
                            body: JSON.stringify({{token: '{token}'}})
                        }});
                        const text = await resp.text();
                        return {{status: resp.status, body: text.substring(0, 300)}};
                    }} catch(e) {{
                        return {{error: e.message}};
                    }}
                }}""")
                print(f"  结果: {response}")
            except Exception as e:
                print(f"  ❌ {e}")
        
        # Step 4: Intercept navigation
        print("\nStep 4: 拦截跳转 URL...")
        print("  请手动点击 OA 卡片，我会拦截跳转 URL...")
        
        async def on_request(request):
            if 'oa.bangcle.com' in request.url or 'sso' in request.url.lower():
                print(f"  🎯 请求: {request.url[:100]}")
                print(f"     类型: {request.resource_type}")
                print(f"     方法: {request.method}")
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
                print(f"  🍪 Cookie 已保存: {len(cookies)} 个")
                break
        
        await browser.close()

asyncio.run(main())

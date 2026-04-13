#!/usr/bin/env python3
"""
OA 登录 - 找到目标 URL 后直接访问
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
        print("找到 OA 卡片目标 URL")
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
        
        print("\nStep 1: 拦截所有网络请求，找到 OA 相关 URL...")
        
        # 拦截所有 fetch/XHR 请求
        oa_urls = []
        
        async def on_response(response):
            url = response.url
            if any(kw in url.lower() for kw in ['oa', 'ecology', 'workflow', 'app', 'entry', 'sso', 'verify']):
                oa_urls.append({
                    'url': url,
                    'status': response.status,
                    'type': response.request.resource_type
                })
        
        page.on("response", on_response)
        
        # 现在手动触发一些操作来获取 URL
        # 尝试点击 OA 文字区域
        try:
            # 找到元素并获取所有属性
            info = await page.evaluate("""() => {
                const all = document.querySelectorAll('*');
                const TARGET = 'OA协同办公平台';
                for (const el of all) {
                    const text = el.textContent?.trim();
                    if (text && text.startsWith(TARGET) && text.length < 200) {
                        // Get all attributes
                        const attrs = {};
                        for (const attr of el.attributes) {
                            attrs[attr.name] = attr.value;
                        }
                        
                        // Also get parent attributes
                        const parentAttrs = {};
                        if (el.parentElement) {
                            for (const attr of el.parentElement.attributes) {
                                parentAttrs[attr.name] = attr.value;
                            }
                        }
                        
                        return {
                            element: attrs,
                            parent: parentAttrs,
                            innerHTML: el.innerHTML.substring(0, 200)
                        };
                    }
                }
                return null;
            }""")
            
            if info:
                print(f"\nOA 元素属性:")
                for k, v in info['element'].items():
                    print(f"  {k}: {v[:100]}")
                print(f"\n父元素属性:")
                for k, v in info['parent'].items():
                    print(f"  {k}: {v[:100]}")
                print(f"\ninnerHTML: {info['innerHTML'][:200]}")
        except Exception as e:
            print(f"  ❌ {e}")
        
        # Step 2: 扫描页面 JS 代码寻找 OA URL
        print("\nStep 2: 扫描 JS 文件寻找 OA URL...")
        
        # Get all script sources
        scripts = await page.evaluate("""() => {
            const scripts = document.querySelectorAll('script[src]');
            return Array.from(scripts).map(s => s.src);
        }""")
        
        print(f"  找到 {len(scripts)} 个 JS 文件")
        
        # Check Vue router configuration
        print("\nStep 3: 尝试 Vue router 方式导航...")
        try:
            # Check if Vue devtools are available
            vue_info = await page.evaluate("""() => {
                // Check for Vue instance
                const app = document.querySelector('#app');
                if (app && app.__vue__) {
                    return {
                        hasVue: true,
                        routes: app.__vue__.$router ? 'yes' : 'no'
                    };
                }
                return {hasVue: false};
            }""")
            print(f"  Vue: {vue_info}")
        except:
            pass
        
        # Step 4: 尝试常见的 SSO URL 模式
        print("\nStep 4: 尝试直接访问 SSO URL...")
        
        sso_urls = [
            'https://oa.bangcle.com/api/ecode/iframe?ssoToken=',
            'https://oa.bangcle.com/api/sso/login',
            'https://oa.bangcle.com/spa/portal/index.html',
            'https://oa.bangcle.com/login/VerifyLoginWeaversso.jsp',
            'https://oa.bangcle.com/wui/index.html#/main',
        ]
        
        # 先获取 IAM token
        iam_token = await page.evaluate("""() => {
            // Check localStorage
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && (key.includes('token') || key.includes('Token') || key.includes('access'))) {
                    return {key: key, value: localStorage.getItem(key)};
                }
            }
            return null;
        }""")
        
        if iam_token:
            print(f"  IAM Token: {iam_token['key']} = {iam_token['value'][:50]}...")
            
            # Try SSO URL with token
            token = iam_token['value']
            test_urls = [
                f'https://oa.bangcle.com/api/sso/login?token={token}',
                f'https://oa.bangcle.com/login/VerifyLoginWeaversso.jsp?token={token}',
            ]
            
            for url in test_urls:
                print(f"\n  尝试: {url[:80]}...")
                response = await page.evaluate(f"""async () => {{
                    try {{
                        const resp = await fetch('{url}', {{
                            method: 'POST',
                            credentials: 'include'
                        }});
                        const data = await resp.json();
                        return {{status: resp.status, data: JSON.stringify(data).substring(0, 200)}};
                    }} catch(e) {{
                        return {{error: e.message}};
                    }}
                }}""")
                print(f"  结果: {response}")
        else:
            print("  未找到 IAM token")
        
        # Step 5: 等待手动操作并拦截 URL
        print("\nStep 5: 等待手动点击，拦截跳转 URL...")
        print("  请在浏览器中点击 OA 卡片...")
        
        # Track URL changes
        prev_url = page.url
        for _ in range(24):  # 2 minutes
            await asyncio.sleep(5)
            url = page.url
            if url != prev_url:
                print(f"\n  URL 变更: {prev_url}")
                print(f"           -> {url}")
                prev_url = url
                
                if 'oa.bangcle.com' in url:
                    print("  ✅ 进入 OA!")
                    cookies = await context.cookies()
                    with open(out + 'oa-working-cookies.json', 'w') as f:
                        json.dump(cookies, f, indent=2)
                    await context.storage_state(path=out + 'oa-working-state.json')
                    await page.screenshot(path=out + 'oa-success.png', full_page=True)
                    print(f"  🍪 Cookie 已保存: {len(cookies)} 个")
                    break
        
        await browser.close()

asyncio.run(main())

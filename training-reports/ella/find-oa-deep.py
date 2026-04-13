#!/usr/bin/env python3
"""
深入分析: 获取 JS 源码，找到 OA 点击事件的目标 URL
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
        print("获取 JS 源码，分析 OA 跳转逻辑")
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
        
        print("\nStep 1: 获取所有 JS 文件并搜索 OA 相关代码...")
        
        # Get all script URLs
        scripts = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
        }""")
        
        print(f"  找到 {len(scripts)} 个 JS 文件:")
        for s in scripts:
            print(f"    {s}")
        
        # Also check for dynamic imports and module files
        all_resources = await page.evaluate("""() => {
            const resources = performance.getEntriesByType('resource');
            return resources
                .filter(r => r.name.includes('.js') && r.name.includes('bangcle'))
                .map(r => r.name);
        }""")
        
        print(f"\n  实际加载的 JS 资源: {len(all_resources)} 个")
        for r in all_resources[:20]:
            print(f"    {r}")
        
        # Step 2: Try to get the Vue app data
        print("\nStep 2: 尝试获取 Vue 应用数据...")
        vue_data = await page.evaluate("""() => {
            // Try multiple ways to find Vue app
            const results = {};
            
            // Way 1: __vue__ on root
            const app = document.querySelector('#app');
            if (app) {
                results.appExists = true;
                results.hasVue = !!app.__vue__;
                if (app.__vue__) {
                    const vue = app.__vue__;
                    results.routes = vue.$router ? Object.keys(vue.$router.options?.routes || {}).length : 0;
                }
            }
            
            // Way 2: __vue_app__
            results.hasVueApp = !!app?.__vue_app__;
            
            // Way 3: Check for app data in window
            for (const key of Object.keys(window)) {
                if (key.includes('vue') || key.includes('Vue') || key.includes('app') || key.includes('App')) {
                    results.windowKeys = results.windowKeys || [];
                    results.windowKeys.push(key);
                }
            }
            
            // Way 4: Check window.__POWERED_BY_QIANKUN__ (micro frontend)
            results.microFrontend = !!window.__POWERED_BY_QIANKUN__;
            results.__INITIAL_STATE__ = !!window.__INITIAL_STATE__;
            
            // Way 5: Check for app data in localStorage/sessionStorage
            results.localStorageKeys = Array.from({length: localStorage.length}, (_, i) => localStorage.key(i));
            results.sessionStorageKeys = Array.from({length: sessionStorage.length}, (_, i) => sessionStorage.key(i));
            
            return results;
        }""")
        
        for k, v in vue_data.items():
            print(f"  {k}: {v}")
        
        # Step 3: Get localStorage data
        print("\nStep 3: 检查 localStorage 数据...")
        storage_data = await page.evaluate("""() => {
            const data = {};
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                const val = localStorage.getItem(key);
                data[key] = val ? val.substring(0, 200) : 'empty';
            }
            return data;
        }""")
        
        for k, v in storage_data.items():
            print(f"  {k}: {v[:100]}")
        
        # Step 4: Fetch and analyze JS files for OA URLs
        print("\nStep 4: 分析 JS 文件内容...")
        
        oa_mentions = []
        for script_url in all_resources[:10]:
            try:
                response = await page.evaluate(f"""async () => {{
                    try {{
                        const resp = await fetch('{script_url}');
                        const text = await resp.text();
                        return {{
                            url: '{script_url}',
                            length: text.length,
                            // Search for OA-related patterns
                            mentions: [
                                ...(text.includes('oa.bangcle.com') ? ['oa.bangcle.com'] : []),
                                ...(text.includes('/wui/') ? ['/wui/'] : []),
                                ...(text.includes('/spa/') ? ['/spa/'] : []),
                                ...(text.includes('ecology') ? ['ecology'] : []),
                                ...(text.includes('协同') ? ['协同'] : []),
                                ...(text.includes('appEntry') ? ['appEntry'] : []),
                                ...(text.includes('appUrl') ? ['appUrl'] : []),
                                ...(text.includes('appLink') ? ['appLink'] : []),
                                ...(text.includes('targetUrl') ? ['targetUrl'] : []),
                                ...(text.includes('redirectUrl') ? ['redirectUrl'] : []),
                                ...(text.includes('sso') ? ['sso'] : []),
                            ]
                        }};
                    }} catch(e) {{
                        return {{url: '{script_url}', error: e.message}};
                    }}
                }}""")
                
                if response.get('mentions') and len(response['mentions']) > 0:
                    print(f"  🎯 {response['url']}")
                    print(f"     提到: {response['mentions']}")
                    oa_mentions.append(response)
                elif response.get('error'):
                    print(f"  ❌ {response['url']}: {response['error']}")
            except Exception as e:
                pass
        
        # Step 5: Check if there's a micro-frontend setup
        print("\nStep 5: 检查微前端架构...")
        micro_info = await page.evaluate("""() => {
            return {
                qiankun: !!window.__POWERED_BY_QIANKUN__,
                initial: !!window.__INITIAL_STATE__,
                microApp: typeof window.microApp !== 'undefined',
                registerMicroApps: typeof window.registerMicroApps !== 'undefined',
                // Check for sub-applications
                subApps: (window.__MICRO_APP_ENVIRONMENT__ || 'not set')
            };
        }""")
        print(f"  微前端信息: {micro_info}")
        
        # Step 6: Look for click handlers on the OA card
        print("\nStep 6: 分析 OA 卡片的点击处理...")
        
        # Get the full HTML structure of the OA card
        card_html = await page.evaluate("""() => {
            const all = document.querySelectorAll('*');
            const TARGET = 'OA协同办公平台';
            for (const el of all) {
                const text = el.textContent?.trim();
                if (text && text.startsWith(TARGET) && text.length < 200) {
                    // Get the full HTML of the card container (go up 5 levels)
                    let node = el;
                    for (let i = 0; i < 5; i++) {
                        if (node.parentElement && node.parentElement.tagName !== 'BODY') {
                            node = node.parentElement;
                        }
                    }
                    return node.outerHTML.substring(0, 2000);
                }
            }
            return null;
        }""")
        
        if card_html:
            print(f"\nOA 卡片 HTML (前 2000 字符):")
            print(card_html[:500])
            
            # Look for onclick or @click attributes
            if '@click' in card_html or 'onclick' in card_html:
                print("\n  ✅ 找到点击处理器!")
            elif 'goTo' in card_html or 'router' in card_html:
                print("\n  ✅ 找到路由跳转!")
        
        # Step 7: Try to simulate the exact mouse event sequence
        print("\nStep 7: 精确模拟鼠标事件序列...")
        
        # Get element bounding box
        box = await page.evaluate("""() => {
            const all = document.querySelectorAll('*');
            const TARGET = 'OA协同办公平台';
            for (const el of all) {
                const text = el.textContent?.trim();
                if (text && text.startsWith(TARGET) && text.length < 200) {
                    const rect = el.getBoundingClientRect();
                    return {
                        x: Math.round(rect.x + rect.width/2),
                        y: Math.round(rect.y + rect.height/2),
                        top: Math.round(rect.top),
                        left: Math.round(rect.left),
                        width: rect.width,
                        height: rect.height
                    };
                }
            }
            return null;
        }""")
        
        if box:
            print(f"  元素位置: ({box['x']},{box['y']}) size={box['width']}x{box['height']}")
            print(f"  顶部位置: ({box['left']},{box['top']})")
            
            # Try clicking at different positions on the element
            positions = [
                (box['x'], box['y']),  # center
                (box['left'] + 20, box['top'] + 20),  # top-left area
                (box['left'] + box['width'] - 20, box['top'] + box['height'] // 2),  # right edge
            ]
            
            for i, (x, y) in enumerate(positions):
                print(f"\n  尝试位置 {i+1}: ({x},{y})")
                
                # Full mouse event sequence
                await page.mouse.move(x, y)
                await asyncio.sleep(0.5)
                await page.mouse.down(x, y)
                await asyncio.sleep(0.3)
                await page.mouse.up(x, y)
                await asyncio.sleep(8)
                
                url = page.url
                print(f"  URL: {url}")
                
                if 'oa.bangcle.com' in url:
                    print("  ✅ 成功!")
                    cookies = await context.cookies()
                    with open(out + 'oa-working-cookies.json', 'w') as f:
                        json.dump(cookies, f, indent=2)
                    await context.storage_state(path=out + 'oa-working-state.json')
                    await page.screenshot(path=out + 'oa-success.png', full_page=True)
                    print("  🍪 已保存")
                    break
        
        # If still failed, keep browser open
        if 'oa.bangcle.com' not in page.url:
            print("\n  浏览器保持打开，请手动点击...")
            for _ in range(24):
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

#!/usr/bin/env python3
"""
OA 卡片点击 - 使用 Playwright 原生 locator + Vue 事件触发
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
        print("OA 卡片点击 - Playwright 原生方案")
        print("=" * 60)
        
        # Login
        print("\nStep 1: 登录 IAM...")
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
        
        print(f"  登录后: {page.url}")
        
        # Go to home
        await page.goto('https://iam.bangcle.com/#/home/index', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(8)
        
        print("\nStep 2: 尝试 Playwright 原生方案...")
        
        success = False
        
        # 方案 1: locator with text
        try:
            print("\n  方案 1: locator(text='OA协同办公平台').click()")
            locator = page.locator("text=OA协同办公平台")
            await locator.first.click(timeout=10000)
            await asyncio.sleep(10)
            print(f"  URL: {page.url}")
            if 'oa.bangcle.com' in page.url:
                success = True
                print("  ✅ 成功!")
        except Exception as e:
            print(f"  ❌ {e}")
        
        if not success:
            # 方案 2: get_by_text + click
            try:
                print("\n  方案 2: get_by_text('OA协同办公平台').click()")
                await page.get_by_text("OA协同办公平台").first.click(timeout=10000)
                await asyncio.sleep(10)
                print(f"  URL: {page.url}")
                if 'oa.bangcle.com' in page.url:
                    success = True
                    print("  ✅ 成功!")
            except Exception as e:
                print(f"  ❌ {e}")
        
        if not success:
            # 方案 3: 找到元素并用 bounding box 点击
            try:
                print("\n  方案 3: bounding box 点击")
                box = await page.evaluate("""() => {
                    const all = document.querySelectorAll('*');
                    for (const el of all) {
                        const text = el.textContent?.trim();
                        if (text && text.includes('OA协同办公平台') && text.length < 200) {
                            const rect = el.getBoundingClientRect();
                            return {
                                x: Math.round(rect.x + rect.width/2),
                                y: Math.round(rect.y + rect.height/2),
                                width: rect.width,
                                height: rect.height,
                                tag: el.tagName
                            };
                        }
                    }
                    return null;
                }""")
                
                if box:
                    print(f"  元素: {box['tag']} at ({box['x']},{box['y']}) size={box['width']}x{box['height']}")
                    await page.mouse.click(box['x'], box['y'])
                    await asyncio.sleep(10)
                    print(f"  URL: {page.url}")
                    if 'oa.bangcle.com' in page.url:
                        success = True
                        print("  ✅ 成功!")
            except Exception as e:
                print(f"  ❌ {e}")
        
        if not success:
            # 方案 4: 通过 Vue 组件查找可点击的卡片容器
            try:
                print("\n  方案 4: 查找 Vue 组件的点击处理")
                result = await page.evaluate("""() => {
                    // Find the card container for OA
                    const all = document.querySelectorAll('[class*="app"], [class*="card"], [class*="item"]');
                    const TARGET = 'OA协同办公平台';
                    const candidates = [];
                    
                    for (const el of all) {
                        const text = el.textContent || '';
                        if (text.includes(TARGET) && text.length < 500 && text.length > 10) {
                            const rect = el.getBoundingClientRect();
                            if (rect.width > 100 && rect.height > 50) {
                                candidates.push({
                                    tag: el.tagName,
                                    className: (el.className || '').substring(0, 60),
                                    width: Math.round(rect.width),
                                    height: Math.round(rect.height),
                                    x: Math.round(rect.x + rect.width/2),
                                    y: Math.round(rect.y + rect.height/2)
                                });
                            }
                        }
                    }
                    return candidates;
                }""")
                
                print(f"  找到 {len(result)} 个候选容器:")
                for i, c in enumerate(result):
                    print(f"    {i+1}. {c['tag']} {c['className'][:40]} {c['width']}x{c['height']} at ({c['x']},{c['y']})")
                
                if result:
                    # Try clicking the first candidate
                    c = result[0]
                    print(f"  点击第一个候选: ({c['x']},{c['y']})")
                    await page.mouse.click(c['x'], c['y'])
                    await asyncio.sleep(10)
                    print(f"  URL: {page.url}")
                    if 'oa.bangcle.com' in page.url:
                        success = True
                        print("  ✅ 成功!")
                    
                    if not success and len(result) > 1:
                        # Try going back to home and clicking second candidate
                        await page.goto('https://iam.bangcle.com/#/home/index', wait_until='networkidle', timeout=30000)
                        await asyncio.sleep(5)
                        c = result[1]
                        print(f"  点击第二个候选: ({c['x']},{c['y']})")
                        await page.mouse.click(c['x'], c['y'])
                        await asyncio.sleep(10)
                        print(f"  URL: {page.url}")
                        if 'oa.bangcle.com' in page.url:
                            success = True
                            print("  ✅ 成功!")
            except Exception as e:
                print(f"  ❌ {e}")
        
        if not success:
            # 方案 5: 查找所有链接和按钮，找到包含 OA 文字的
            try:
                print("\n  方案 5: 查找包含 OA 的链接/按钮")
                links = await page.evaluate("""() => {
                    const elements = document.querySelectorAll('a, button, [role="button"], [onclick]');
                    const TARGET = 'OA协同办公平台';
                    const found = [];
                    for (const el of elements) {
                        const text = el.textContent?.trim() || '';
                        if (text.includes('OA') || text.includes('协同') || text.includes('办公')) {
                            const rect = el.getBoundingClientRect();
                            found.push({
                                tag: el.tagName,
                                text: text.substring(0, 60),
                                href: el.getAttribute('href') || '',
                                x: Math.round(rect.x + rect.width/2),
                                y: Math.round(rect.y + rect.height/2),
                                width: rect.width,
                                height: rect.height
                            });
                        }
                    }
                    return found;
                }""")
                
                print(f"  找到 {len(links)} 个相关元素:")
                for i, l in enumerate(links):
                    print(f"    {i+1}. {l['tag']} '{l['text'][:40]}' href={l['href']} at ({l['x']},{l['y']})")
                
                if links:
                    await page.mouse.click(links[0]['x'], links[0]['y'])
                    await asyncio.sleep(10)
                    print(f"  URL: {page.url}")
                    if 'oa.bangcle.com' in page.url:
                        success = True
                        print("  ✅ 成功!")
            except Exception as e:
                print(f"  ❌ {e}")
        
        # Final check
        print("\n" + "=" * 60)
        if 'oa.bangcle.com' in page.url and 'iam' not in page.url:
            print("✅ 成功进入 OA!")
            cookies = await context.cookies()
            with open(out + 'oa-working-cookies.json', 'w') as f:
                json.dump(cookies, f, indent=2)
            await context.storage_state(path=out + 'oa-working-state.json')
            await page.screenshot(path=out + 'oa-success.png', full_page=True)
            print(f"  🍪 Cookie 已保存: {len(cookies)} 个")
        else:
            print("⚠️ 仍未跳转到 OA")
            await page.screenshot(path=out + 'oa-final-attempt.png', full_page=True)
            print("  浏览器保持打开，请手动点击 OA 卡片")
            
            # Wait for manual operation
            for _ in range(12):
                await asyncio.sleep(5)
                url = page.url
                if 'oa.bangcle.com' in url and 'iam' not in url:
                    print(f"\n  检测到手动跳转! URL: {url}")
                    cookies = await context.cookies()
                    with open(out + 'oa-working-cookies.json', 'w') as f:
                        json.dump(cookies, f, indent=2)
                    await context.storage_state(path=out + 'oa-working-state.json')
                    await page.screenshot(path=out + 'oa-success.png', full_page=True)
                    print("  🍪 Cookie 已保存")
                    break
        
        await browser.close()

asyncio.run(main())

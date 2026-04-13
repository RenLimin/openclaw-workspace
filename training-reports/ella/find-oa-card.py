#!/usr/bin/env python3
"""
精准定位并点击 IAM 首页的 OA 应用卡片
"""

import asyncio
import json
from playwright.async_api import async_playwright

JS_ANALYZE = """
() => {
    const result = [];
    const all = document.querySelectorAll('*');
    const TARGET = 'OA协同办公平台';
    
    for (const el of all) {
        const text = el.textContent?.trim();
        if (text && text.startsWith(TARGET)) {
            let node = el;
            for (let depth = 0; depth < 10 && node; depth++) {
                const style = window.getComputedStyle(node);
                const rect = node.getBoundingClientRect();
                result.push({
                    depth: depth,
                    tag: node.tagName,
                    className: (node.className || '').substring(0, 100),
                    id: node.id || '',
                    cursor: style.cursor,
                    width: Math.round(rect.width),
                    height: Math.round(rect.height),
                    isA: node.tagName === 'A',
                    href: node.getAttribute('href') || '',
                    role: node.getAttribute('role') || '',
                    tabindex: node.getAttribute('tabindex') || '',
                    dataApp: node.getAttribute('data-app') || '',
                    onclick: node.getAttribute('onclick') ? 'yes' : '',
                    pointerEvents: style.pointerEvents,
                    textPreview: (node.textContent || '').substring(0, 80).replace(/\\n/g, ' ')
                });
                node = node.parentElement;
            }
            break;
        }
    }
    return result;
}
"""

JS_CLICK_DEPTH = """(depth) => {
    const all = document.querySelectorAll('*');
    const TARGET = 'OA协同办公平台';
    
    for (const el of all) {
        const text = el.textContent?.trim();
        if (text && text.startsWith(TARGET)) {
            let node = el;
            for (let d = 0; d < depth; d++) {
                if (node.parentElement) node = node.parentElement;
            }
            const rect = node.getBoundingClientRect();
            node.click();
            return {
                clicked: node.tagName + ' depth=' + depth,
                size: rect.width + 'x' + rect.height,
                url: window.location.href
            };
        }
    }
    return {clicked: 'not found'};
}
"""

JS_CLICK_MOUSE_EVENTS = """(depth) => {
    const all = document.querySelectorAll('*');
    const TARGET = 'OA协同办公平台';
    
    for (const el of all) {
        const text = el.textContent?.trim();
        if (text && text.startsWith(TARGET)) {
            let node = el;
            for (let d = 0; d < depth; d++) {
                if (node.parentElement) node = node.parentElement;
            }
            const rect = node.getBoundingClientRect();
            
            // Dispatch multiple event types
            const events = [
                new MouseEvent('mousedown', { view: window, bubbles: true, cancelable: true, clientX: rect.left + rect.width/2, clientY: rect.top + rect.height/2 }),
                new MouseEvent('mouseup', { view: window, bubbles: true, cancelable: true, clientX: rect.left + rect.width/2, clientY: rect.top + rect.height/2 }),
                new MouseEvent('click', { view: window, bubbles: true, cancelable: true, clientX: rect.left + rect.width/2, clientY: rect.top + rect.height/2 }),
            ];
            
            for (const evt of events) {
                node.dispatchEvent(evt);
            }
            
            return {
                dispatched: node.tagName + ' depth=' + depth,
                url: window.location.href
            };
        }
    }
    return {dispatched: 'not found'};
}
"""

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
        print("精准定位 OA 应用卡片")
        print("=" * 60)
        
        # Step 1: Login
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
                print("  等待登录...")
                await asyncio.sleep(10)
        
        print(f"  登录后: {page.url}")
        
        # Step 2: Go to home
        print("\nStep 2: 确保在首页...")
        await page.goto('https://iam.bangcle.com/#/home/index', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(8)
        print(f"  URL: {page.url}")
        
        # Step 3: Analyze DOM
        print("\nStep 3: DOM 分析...")
        analysis = await page.evaluate(JS_ANALYZE)
        
        print(f"\n找到 {len(analysis)} 层 DOM 节点:")
        print(f"{'Depth':<6} {'Tag':<8} {'Size':<12} {'Cursor':<12} {'Class':<40}")
        print("-" * 80)
        for node in analysis:
            print(f"{node['depth']:<6} {node['tag']:<8} {node['width']}x{node['height']:<7} {node['cursor']:<12} {node['className'][:38]}")
            if node['href']:
                print(f"       href={node['href']}")
            if node['dataApp']:
                print(f"       data-app={node['dataApp']}")
            if node['role']:
                print(f"       role={node['role']}")
        
        # Step 4: Find best clickable depth
        print("\nStep 4: 尝试点击...")
        
        best_depth = 0
        for node in analysis:
            if node['cursor'] == 'pointer' or node['isA'] or node['role'] == 'button':
                best_depth = node['depth']
                print(f"  找到可点击节点: depth={best_depth}, {node['tag']}")
                break
            if node['href']:
                best_depth = node['depth']
                print(f"  找到链接节点: depth={best_depth}, href={node['href']}")
                break
        
        if not any(n['cursor'] == 'pointer' or n['isA'] or n['href'] for n in analysis):
            print("  未找到明显的可点击标记，尝试 depth=3,4,5...")
            depths_to_try = [3, 4, 5, 6, 2]
        else:
            depths_to_try = [best_depth]
        
        success = False
        for depth in depths_to_try:
            print(f"\n  尝试 depth={depth}...")
            
            # Normal click
            result = await page.evaluate(JS_CLICK_DEPTH, depth)
            print(f"    click: {result.get('clicked', 'error')}")
            await asyncio.sleep(8)
            url = page.url
            print(f"    URL: {url}")
            
            if 'oa.bangcle.com' in url and 'iam' not in url:
                print("  ✅ 成功!")
                success = True
                break
            
            # Mouse events
            print(f"  尝试 dispatch 事件 depth={depth}...")
            result = await page.evaluate(JS_CLICK_MOUSE_EVENTS, depth)
            print(f"    dispatch: {result.get('dispatched', 'error')}")
            await asyncio.sleep(8)
            url = page.url
            print(f"    URL: {url}")
            
            if 'oa.bangcle.com' in url and 'iam' not in url:
                print("  ✅ 成功!")
                success = True
                break
        
        if not success:
            print("\n  所有尝试均失败")
            print("  浏览器保持打开，请手动点击 OA 卡片")
            await page.screenshot(path=out + 'oa-dom-analysis.png', full_page=True)
            print("  📸 截图已保存")
            
            # Wait for manual click
            for _ in range(12):  # 60 seconds
                await asyncio.sleep(5)
                url = page.url
                if 'oa.bangcle.com' in url and 'iam' not in url:
                    print(f"\n  检测到手动跳转! URL: {url}")
                    success = True
                    break
        
        if success:
            print("\n" + "=" * 60)
            print("✅ 成功进入 OA!")
            print("=" * 60)
            
            cookies = await context.cookies()
            with open(out + 'oa-working-cookies.json', 'w') as f:
                json.dump(cookies, f, indent=2)
            await context.storage_state(path=out + 'oa-working-state.json')
            await page.screenshot(path=out + 'oa-success.png', full_page=True)
            print(f"  🍪 Cookie 已保存: {len(cookies)} 个")
            
            for c in cookies:
                print(f"    {c['name']}: domain={c.get('domain', 'N/A')}")
        
        await browser.close()

asyncio.run(main())

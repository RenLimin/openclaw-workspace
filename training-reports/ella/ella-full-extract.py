#!/usr/bin/env python3
"""
Ella 合同管理 - 完整数据提取脚本
1. 使用 OA cookies 登录
2. 搜索合同台账 XSZS2604020200
3. 提取合同详情全文
4. 下载合同附件 PDF
5. 提取签章页图片
6. 提取审批流程记录
"""

import asyncio
import json
import os
import time
from playwright.async_api import async_playwright

OUT_DIR = '/Users/bangcle/.openclaw/agents/ella/workspace/training-reports/'
COOKIE_FILE = '/Users/bangcle/.openclaw/workspace/training-reports/ella/oa-working-cookies.json'
STATE_FILE = '/Users/bangcle/.openclaw/workspace/training-reports/ella/oa-working-state.json'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        # Load storage state (includes cookies)
        if os.path.exists(STATE_FILE):
            print("Loading storage state...")
            context2 = await browser.new_context(
                storage_state=STATE_FILE,
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            await context.close()
            context = context2
        
        page = await context.new_page()
        
        # Step 1: Verify OA session
        print("\n=== Step 1: Verify OA session ===")
        await page.goto('https://oa.bangcle.com/wui/index.html#/main/cs/app/e6637c94b5a247bf853ae9000b6f8e74_CompanyPortal?menuIds=0,240&menuPathIds=0,240&_key=sdyfd2', 
                       wait_until='networkidle', timeout=30000)
        await asyncio.sleep(3)
        print(f"  Current URL: {page.url}")
        await page.screenshot(path=OUT_DIR + 'oa-verify.png', full_page=True)
        
        # Step 2: Navigate to contract ledger (customid=179)
        print("\n=== Step 2: Navigate to contract ledger ===")
        contract_url = 'https://oa.bangcle.com/spa/apps/Custom/179'
        await page.goto(contract_url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(5)
        print(f"  Contract ledger URL: {page.url}")
        await page.screenshot(path=OUT_DIR + 'contract-ledger-page.png', full_page=True)
        
        # Get page text
        text = await page.inner_text('body')
        with open(OUT_DIR + 'contract-ledger-text.txt', 'w') as f:
            f.write(text)
        print(f"  Page text length: {len(text)}")
        
        # Step 3: Search for XSZS2604020200
        print("\n=== Step 3: Search for XSZS26040200 ===")
        
        # Try to find search input
        search_inputs = await page.query_selector_all('input[placeholder*="搜索"], input[placeholder*="search"], input[type="search"]')
        if not search_inputs:
            search_inputs = await page.query_selector_all('input')
        
        search_input = None
        for inp in search_inputs:
            placeholder = await inp.get_attribute('placeholder') or ''
            visible = await inp.is_visible()
            if visible and any(kw in placeholder.lower() for kw in ['搜索', 'search', '关键词', '合同编号']):
                search_input = inp
                break
        
        if not search_input and search_inputs:
            search_input = search_inputs[0]
        
        if search_input:
            print("  Found search input, entering contract number...")
            await search_input.fill('XSZS2604020200')
            await asyncio.sleep(2)
            
            # Try to click search button
            search_btn = page.locator('button:has-text("搜索"), button:has-text("查询"), [data-role="searchBtn"]')
            if await search_btn.count() > 0:
                await search_btn.first.click()
            else:
                await search_input.press('Enter')
            await asyncio.sleep(5)
            
            await page.screenshot(path=OUT_DIR + 'contract-search-result.png', full_page=True)
            search_text = await page.inner_text('body')
            with open(OUT_DIR + 'contract-search-text.txt', 'w') as f:
                f.write(search_text)
            print(f"  Search result text length: {len(search_text)}")
            
            # Check if we see the contract number in results
            if 'XSZS2604020200' in search_text:
                print("  ✅ Found XSZS2604020200 in search results")
            else:
                print("  ⚠️ XSZS2604020200 not found in search results")
                print(f"  First 500 chars: {search_text[:500]}")
        else:
            print("  ⚠️ No search input found")
        
        # Step 4: Try API approach - get contract detail via API
        print("\n=== Step 4: Try API approach ===")
        
        # Get cookies for API calls
        cookies = await context.cookies()
        oa_cookies = {c['name']: c['value'] for c in cookies if 'oa.bangcle.com' in c.get('domain', '')}
        print(f"  OA cookies: {list(oa_cookies.keys())}")
        
        # Try to get contract detail via API
        # The custom page usually has an API endpoint
        api_urls_to_try = [
            f'https://oa.bangcle.com/api/custom/data/list?customId=179&pageSize=10&pageNumber=1&keyword=XSZS2604020200',
            f'https://oa.bangcle.com/spa/api/custom/data/list?customId=179&pageSize=10&pageNumber=1&keyword=XSZS2604020200',
            f'https://oa.bangcle.com/api/custom/179/list?pageSize=10&pageNumber=1&keyword=XSZS2604020200',
        ]
        
        headers = {
            'Cookie': '; '.join([f'{k}={v}' for k, v in oa_cookies.items()]),
            'Accept': 'application/json',
            'Referer': contract_url,
        }
        
        for api_url in api_urls_to_try:
            print(f"\n  Trying: {api_url}")
            response = await page.evaluate(f"""async () => {{
                const resp = await fetch('{api_url}', {{
                    headers: {{
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    }}
                }});
                const text = await resp.text();
                return {{status: resp.status, text: text.substring(0, 2000)}};
            }}""")
            print(f"  Status: {response['status']}, Response: {response['text'][:200]}")
            if response['status'] == 200 and 'XSZS2604020200' in response['text']:
                with open(OUT_DIR + 'api-contract-search.json', 'w') as f:
                    f.write(response['text'])
                print("  ✅ Got contract data from API!")
                break
        
        # Step 5: Try to find and click the contract detail link
        print("\n=== Step 5: Try to find contract detail link ===")
        
        # Look for any link or element containing the contract number
        links = await page.query_selector_all('a')
        for link in links:
            href = await link.get_attribute('href') or ''
            text_content = await link.inner_text()
            if 'XSZS2604020200' in text_content or 'XSZS2604020200' in href:
                print(f"  Found link: text='{text_content}', href='{href}'")
                # Check if it opens a new window/tab
                target = await link.get_attribute('target')
                if target == '_blank':
                    async with context.expect_page() as new_page_info:
                        await link.click()
                    new_page = await new_page_info.value
                    await new_page.wait_for_load_state('networkidle', timeout=30000)
                    await asyncio.sleep(5)
                    print(f"  New page URL: {new_page.url}")
                    await new_page.screenshot(path=OUT_DIR + 'contract-detail-new-tab.png', full_page=True)
                    detail_text = await new_page.inner_text('body')
                    with open(OUT_DIR + 'contract-detail-full.txt', 'w') as f:
                        f.write(detail_text)
                    print(f"  Detail text length: {len(detail_text)}")
                break
        
        # Step 6: Look for iframe content (contract details often in iframe)
        print("\n=== Step 6: Check for iframes ===")
        frames = page.frames
        for frame in frames:
            if frame != page.main_frame:
                frame_url = frame.url
                frame_name = frame.name
                print(f"  Frame: name='{frame_name}', url='{frame_url}'")
                try:
                    frame_text = await frame.inner_text('body')
                    if len(frame_text) > 100:
                        print(f"  Frame text length: {len(frame_text)}")
                        if 'XSZS2604020200' in frame_text:
                            print("  ✅ Found contract data in iframe!")
                            with open(OUT_DIR + 'contract-iframe-text.txt', 'w') as f:
                                f.write(frame_text)
                except Exception as e:
                    print(f"  Frame text error: {e}")
        
        # Step 7: Get full page HTML for analysis
        print("\n=== Step 7: Save full HTML ===")
        html = await page.content()
        with open(OUT_DIR + 'contract-ledger-full.html', 'w') as f:
            f.write(html)
        print(f"  HTML length: {len(html)}")
        
        # Step 8: Dump all network responses for analysis
        print("\n=== Step 8: Intercept network ===")
        
        # Set up response listener
        responses = []
        page.on('response', lambda resp: responses.append({
            'url': resp.url,
            'status': resp.status,
            'type': resp.request.resource_type
        }))
        
        # Refresh the page to capture network requests
        await page.reload(wait_until='networkidle', timeout=30000)
        await asyncio.sleep(5)
        
        for r in responses:
            if 'custom' in r['url'].lower() or '179' in r['url']:
                print(f"  {r['status']} {r['type']} {r['url'][:120]}")
        
        # Save all response URLs
        with open(OUT_DIR + 'network-responses.json', 'w') as f:
            json.dump(responses, f, indent=2, ensure_ascii=False)
        
        print("\n=== Done ===")
        await browser.close()

asyncio.run(main())

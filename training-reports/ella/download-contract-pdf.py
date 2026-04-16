#!/usr/bin/env python3
"""
下载合同附件 PDF 并提取内容
"""

import asyncio
import json
import os
import time
from playwright.async_api import async_playwright

OUT_DIR = '/Users/bangcle/.openclaw/agents/ella/workspace/training-reports/'
STATE_FILE = '/Users/bangcle/.openclaw/workspace/training-reports/ella/oa-working-state.json'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            storage_state=STATE_FILE,
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = await context.new_page()
        
        print("=" * 60)
        print("Step 1: Navigate to OA contract ledger")
        print("=" * 60)
        
        # Navigate to contract ledger
        await page.goto('https://oa.bangcle.com/wui/index.html#/main/cs/app/e6637c94b5a247bf853ae9000b6f8e74_CompanyPortal?menuIds=0,240&menuPathIds=0,240&_key=sdyfd2',
                       wait_until='networkidle', timeout=30000)
        await asyncio.sleep(3)
        print(f"  OA Portal URL: {page.url}")
        
        # Navigate to contract custom page
        await page.goto('https://oa.bangcle.com/spa/cube/index.html', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(5)
        
        # The contract detail link from previous data:
        # javascript:cubeOpenHref("/spa/cube/index.html#/main/cube/card?type=0&modeId=112&formId=-249&billid=14242...")
        # Try to navigate directly to the contract detail
        contract_detail_url = 'https://oa.bangcle.com/spa/cube/index.html#/main/cube/card?type=0&modeId=112&formId=-249&billid=14242'
        print(f"\n  Navigating to contract detail: {contract_detail_url}")
        await page.goto(contract_detail_url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(8)
        
        print(f"  Current URL: {page.url}")
        await page.screenshot(path=OUT_DIR + 'contract-detail-page.png', full_page=True)
        
        # Get all text
        detail_text = await page.inner_text('body')
        with open(OUT_DIR + 'contract-detail-new.txt', 'w') as f:
            f.write(detail_text)
        print(f"  Detail text length: {len(detail_text)}")
        
        # Check if we see the contract number
        if 'XSZS2604020200' in detail_text:
            print("  ✅ Found XSZS2604020200 in page")
        else:
            print("  ⚠️ XSZS2604020200 not found")
            print(f"  First 300 chars: {detail_text[:300]}")
        
        # Look for iframes (attachment might be in iframe)
        print("\n  Checking iframes...")
        for frame in page.frames:
            if frame != page.main_frame:
                furl = frame.url
                ftitle = frame.title or ''
                print(f"  Frame: url={furl[:80]}, title={ftitle[:50]}")
                try:
                    ftext = await frame.inner_text('body')
                    print(f"    Text length: {len(ftext)}")
                    if len(ftext) > 200:
                        with open(OUT_DIR + 'iframe-text-frame-' + str(frame.frames.index(frame) if hasattr(frame, 'frames') else '0') + '.txt', 'w') as f:
                            f.write(ftext)
                except:
                    pass
        
        # Look for PDF links
        print("\n  Looking for PDF links...")
        links = await page.query_selector_all('a')
        for link in links:
            href = await link.get_attribute('href') or ''
            text = await link.inner_text()
            if '.pdf' in href.lower() or '.pdf' in text.lower() or '南京帮易' in text:
                print(f"  PDF link: text='{text[:50]}', href='{href[:100]}'")
        
        # Try to evaluate the page to find attachment links
        attachment_info = await page.evaluate("""() => {
            const results = [];
            const allLinks = document.querySelectorAll('a');
            allLinks.forEach(a => {
                const href = a.getAttribute('href') || '';
                const text = a.textContent || '';
                if (href.includes('.pdf') || text.includes('.pdf') || text.includes('南京帮易') || text.includes('脱敏')) {
                    results.push({ text: text.trim(), href: href });
                }
            });
            // Also check for attachment elements
            const attachments = document.querySelectorAll('[class*="attach"], [class*="附件"]');
            attachments.forEach(el => {
                results.push({ tag: el.tagName, class: el.className, text: el.textContent.trim().substring(0, 200) });
            });
            return results;
        }""")
        print(f"  Found {len(attachment_info)} attachment elements")
        for item in attachment_info:
            print(f"  {item}")
        
        # Save full HTML
        html = await page.content()
        with open(OUT_DIR + 'contract-detail-full-new.html', 'w') as f:
            f.write(html)
        print(f"  Saved HTML: {len(html)} bytes")
        
        # Try to find the contract info page (billid=14242) via API
        print("\n  Trying API calls...")
        
        api_calls = [
            f'https://oa.bangcle.com/api/custom/card/data?billId=14242&modeId=112',
            f'https://oa.bangcle.com/api/custom/data/detail?billId=14242&modeId=112',
            f'https://oa.bangcle.com/api/custom/112/detail?billId=14242',
        ]
        
        for api_url in api_calls:
            print(f"  Trying: {api_url}")
            try:
                response = await page.evaluate(f"""async () => {{
                    const resp = await fetch('{api_url}', {{
                        headers: {{ 'Accept': 'application/json' }}
                    }});
                    const text = await resp.text();
                    return {{status: resp.status, text: text.substring(0, 3000)}};
                }}""")
                print(f"    Status: {response['status']}, Response: {response['text'][:200]}")
            except Exception as e:
                print(f"    Error: {e}")
        
        # Try to find attachment download links via page JS
        print("\n  Looking for attachment download links via JS...")
        attach_data = await page.evaluate("""() => {
            // Look for global variables that might contain attachment info
            const vars = Object.keys(window).filter(k => 
                k.toLowerCase().includes('attach') || 
                k.toLowerCase().includes('bill') || 
                k.toLowerCase().includes('contract') ||
                k.toLowerCase().includes('custom')
            );
            return vars.map(k => {
                try {
                    const v = window[k];
                    if (typeof v === 'object' && v !== null) {
                        return { key: k, type: typeof v, sample: JSON.stringify(v).substring(0, 300) };
                    }
                    return { key: k, type: typeof v, value: String(v).substring(0, 100) };
                } catch(e) {
                    return { key: k, type: 'error' };
                }
            });
        }""")
        for item in attach_data:
            print(f"  {item['key']}: {item['type']}")
        
        # Try to find attachment API endpoints from network
        print("\n  Looking for attachment-related network requests...")
        responses = []
        page.on('response', lambda resp: responses.append({
            'url': resp.url,
            'status': resp.status,
            'type': resp.request.resource_type
        }))
        
        # Reload to capture
        await page.reload(wait_until='networkidle', timeout=30000)
        await asyncio.sleep(5)
        
        for r in responses:
            if any(kw in r['url'].lower() for kw in ['attach', 'bill', '14242', 'pdf', 'download', 'custom']):
                print(f"  {r['status']} {r['type']} {r['url'][:150]}")
        
        with open(OUT_DIR + 'network-responses-new.json', 'w') as f:
            json.dump(responses, f, indent=2, ensure_ascii=False)
        
        print("\n=== Done ===")
        await browser.close()

asyncio.run(main())

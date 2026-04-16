#!/usr/bin/env python3
"""
Ella 合同管理 - 最终数据提取
下载 PDF 附件、提取签章页、生成最终输出
"""

import asyncio
import json
import os
import re
from playwright.async_api import async_playwright

OUT = '/Users/bangcle/.openclaw/agents/ella/workspace/training-reports/'
STATE = '/Users/bangcle/.openclaw/workspace/training-reports/ella/oa-working-state.json'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        ctx = await browser.new_context(storage_state=STATE, viewport={'width': 1920, 'height': 1080})
        page = await ctx.new_page()
        
        # Navigate to contract detail page
        print("Navigating to contract detail...")
        url = 'https://oa.bangcle.com/spa/cube/index.html#/main/cube/card?type=0&modeId=112&formId=-249&billid=14242'
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await asyncio.sleep(8)
        
        # Save page HTML
        html = await page.content()
        with open(OUT + 'contract-detail-final.html', 'w') as f:
            f.write(html)
        print(f"HTML saved: {len(html)} bytes")
        
        # Look for attachment download links
        print("\nSearching for PDF attachment links...")
        attach_links = await page.evaluate("""() => {
            const results = [];
            // Search all elements for PDF references
            const all = document.querySelectorAll('*');
            all.forEach(el => {
                const text = el.textContent || '';
                if (text.includes('.pdf') || text.includes('南京帮易') || text.includes('脱敏')) {
                    results.push({
                        tag: el.tagName,
                        text: text.trim().substring(0, 300),
                        href: el.getAttribute('href') || '',
                        onclick: (el.getAttribute('onclick') || '').substring(0, 200),
                        style: (el.getAttribute('style') || '').substring(0, 100)
                    });
                }
            });
            // Also check iframe content
            const iframes = document.querySelectorAll('iframe');
            iframes.forEach((f, i) => {
                results.push({iframe: i, src: f.src});
            });
            return results;
        }""")
        for item in attach_links:
            print(f"  {item}")
        
        # Try API calls to get attachment data
        print("\nTrying attachment APIs...")
        apis = [
            'https://oa.bangcle.com/api/attachment/list?billId=14242&modeId=112',
            'https://oa.bangcle.com/api/formmode/attachment?billId=14242',
            'https://oa.bangcle.com/api/custom/attachment?billId=14242&modeId=112',
            'https://oa.bangcle.com/api/file/list?billId=14242',
            'https://oa.bangcle.com/spa/api/attachment/list?billId=14242&modeId=112',
        ]
        for api in apis:
            print(f"  Trying: {api}")
            try:
                resp = await page.evaluate(f"""async () => {{
                    try {{
                        const r = await fetch('{api}', {{headers: {{'Accept': 'application/json'}}}});
                        return {{status: r.status, text: (await r.text()).substring(0, 1000)}};
                    }} catch(e) {{
                        return {{error: e.message}};
                    }}
                }}""")
                print(f"    Result: {resp}")
            except Exception as e:
                print(f"    Error: {e}")
        
        # Look for any clickable elements that might be attachment download buttons
        print("\nLooking for attachment buttons...")
        buttons = await page.query_selector_all('button, [role="button"], a[onclick]')
        for btn in buttons:
            text = await btn.inner_text()
            if text and any(kw in text for kw in ['附件', '下载', 'PDF', '帮易', '脱敏']):
                print(f"  Button: '{text}'")
        
        # Check for table/field with attachment info
        print("\nLooking for attachment fields in page text...")
        text = await page.inner_text('body')
        if '南京帮易' in text:
            print("  ✅ Found '南京帮易' in page text")
            idx = text.find('南京帮易')
            print(f"  Context: ...{text[max(0,idx-100):idx+200]}...")
        if '.pdf' in text.lower():
            print("  ✅ Found PDF reference in text")
            idx = text.lower().find('.pdf')
            print(f"  Context: ...{text[max(0,idx-100):idx+200]}...")
        
        # Extract full text for parsing
        with open(OUT + 'contract-detail-final-text.txt', 'w') as f:
            f.write(text)
        print(f"\nFull text saved: {len(text)} chars")
        
        # Check iframes
        print("\nChecking iframes...")
        for i, frame in enumerate(page.frames):
            if frame != page.main_frame:
                furl = frame.url or ''
                fname = frame.name or ''
                print(f"  Frame {i}: url={furl[:100]}, name={fname}")
                try:
                    ftext = await frame.inner_text('body')
                    if len(ftext) > 50:
                        print(f"    Text length: {len(ftext)}")
                        if '.pdf' in ftext.lower() or '南京帮易' in ftext or '脱敏' in ftext:
                            print(f"    ✅ Found PDF reference in iframe!")
                            with open(OUT + f'iframe-{i}.txt', 'w') as f:
                                f.write(ftext)
                except:
                    pass
        
        # Screenshot
        await page.screenshot(path=OUT + 'contract-detail-final.png', full_page=True)
        print("\nScreenshot saved")
        
        # Check for network requests related to attachments
        print("\nIntercepting network for attachment requests...")
        responses = []
        def on_response(resp):
            url = resp.url
            if any(kw in url.lower() for kw in ['attach', 'pdf', 'download', 'file', '14242', 'custom']):
                responses.append({'url': url, 'status': resp.status, 'type': resp.request.resource_type})
        
        page.on('response', on_response)
        await page.reload(wait_until='networkidle', timeout=30000)
        await asyncio.sleep(5)
        
        for r in responses:
            print(f"  {r['status']} {r['type']} {r['url'][:150]}")
        
        with open(OUT + 'network-final.json', 'w') as f:
            json.dump(responses, f, indent=2, ensure_ascii=False)
        
        print("\n=== Done ===")
        await browser.close()

asyncio.run(main())

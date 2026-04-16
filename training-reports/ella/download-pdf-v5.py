#!/usr/bin/env python3
"""
Download PDF - wait longer for SPA to render, then click download.
"""
import json
import os
from playwright.sync_api import sync_playwright

STATE_FILE = '/Users/bangcle/.openclaw/workspace/training-reports/ella/oa-working-state.json'
OUTPUT_DIR = '/Users/bangcle/.openclaw/agents/ella/workspace/training-reports'
FILE_ID = '205115'

def main():
    with open(STATE_FILE) as f:
        state = json.load(f)
    print(f'Loaded {len(state.get("cookies", []))} cookies')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        context = browser.new_context(
            storage_state=STATE_FILE,
            accept_downloads=True,
            viewport={'width': 1440, 'height': 900},
        )
        page = context.new_page()
        downloaded_path = None

        # Intercept ALL responses
        captured_urls = []
        def handle_response(response):
            url = response.url
            ct = response.headers.get('content-type', '')
            status = response.status
            captured_urls.append({
                'url': url[:150],
                'ct': ct[:60],
                'status': status,
                'size': len(response.body()) if response.body_size else '?'
            })

        page.on('response', handle_response)

        try:
            # Go to OA home first
            print('\n[1] Navigating to OA home...')
            resp = page.goto('https://oa.bangcle.com/', wait_until='networkidle', timeout=60000)
            print(f'Status: {resp.status}, URL: {page.url}')
            page.wait_for_timeout(5000)
            page.screenshot(path=os.path.join(OUTPUT_DIR, '01-oa-home.png'))
            
            # Check page content
            content = page.content()
            print(f'Page content length: {len(content)}')
            if '登录' in content[:1000] or 'login' in content[:500].lower():
                print('❌ Login page detected')
                return
            if len(content) < 1000:
                print('⚠️ Very short page content - might be blank')
            else:
                print(f'First 300 chars: {content[:300]}')

            # Navigate to contract detail
            print('\n[2] Navigating to contract detail...')
            contract_url = 'https://oa.bangcle.com/spa/cube/#/customPage?customid=179&mainTableDataId=14242'
            page.goto(contract_url, wait_until='networkidle', timeout=60000)
            page.wait_for_timeout(10000)
            
            page.screenshot(path=os.path.join(OUTPUT_DIR, '02-contract-page.png'))
            print(f'Page URL: {page.url}')
            
            content = page.content()
            print(f'Page content length: {len(content)}')
            
            # Check for specific elements
            has_table = 'excelMainTable' in content
            has_download = 'icon-coms-download' in content or 'wea-field-link' in content
            has_脱敏 = '脱敏' in content
            print(f'Has table: {has_table}, Has download: {has_download}, Has 脱敏: {has_脱敏}')

            if has_脱敏 or has_download:
                # Find download icon
                download_icons = page.query_selector_all('.icon-coms-download')
                print(f'Found {len(download_icons)} download icons')
                
                file_links = page.query_selector_all('a.wea-field-link')
                print(f'Found {len(file_links)} file links')
                for link in file_links:
                    title = link.get_attribute('title')
                    print(f'  Link title: {title}')

                # Try clicking download icon
                if download_icons:
                    print('\n[3] Clicking download icon...')
                    with page.expect_download(timeout=20000) as dl_info:
                        download_icons[0].click()
                    download = dl_info.value
                    save_path = os.path.join(OUTPUT_DIR, download.suggested_filename() or 'XSZS2604020200脱敏.pdf')
                    download.save_as(save_path)
                    size = os.path.getsize(save_path)
                    print(f'Saved: {save_path} ({size} bytes)')
                    
                    # Verify PDF
                    with open(save_path, 'rb') as f:
                        header = f.read(10)
                    if header[:4] == b'%PDF':
                        print(f'✅ Confirmed PDF')
                        downloaded_path = save_path
                    else:
                        print(f'⚠️ Not a PDF: {header}')
                        with open(save_path, 'r', errors='replace') as f:
                            print(f'Content: {f.read(300)}')

                elif file_links:
                    print('\n[3] Clicking file link...')
                    for link in file_links:
                        title = link.get_attribute('title')
                        if title and '.pdf' in title:
                            with page.expect_download(timeout=20000) as dl_info:
                                link.click()
                            download = dl_info.value
                            save_path = os.path.join(OUTPUT_DIR, download.suggested_filename() or 'XSZS2604020200脱敏.pdf')
                            download.save_as(save_path)
                            size = os.path.getsize(save_path)
                            print(f'Saved: {save_path} ({size} bytes)')
                            with open(save_path, 'rb') as f:
                                header = f.read(10)
                            if header[:4] == b'%PDF':
                                print(f'✅ Confirmed PDF')
                                downloaded_path = save_path
                            break
                else:
                    print('❌ No download elements found on page')
                    # Try scrolling
                    print('Scrolling down...')
                    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    page.wait_for_timeout(3000)
                    page.screenshot(path=os.path.join(OUTPUT_DIR, '02-scrolled.png'))
                    
                    download_icons = page.query_selector_all('.icon-coms-download')
                    print(f'After scroll: {len(download_icons)} download icons')
            else:
                print('❌ Page does not contain expected content')
                # Try to find any links
                all_links = page.query_selector_all('a')
                print(f'Total links on page: {len(all_links)}')
                for link in all_links[:10]:
                    href = link.get_attribute('href')
                    text = link.inner_text()[:50]
                    print(f'  {text}: {href[:80] if href else "(no href)"}')

            page.screenshot(path=os.path.join(OUTPUT_DIR, '03-final.png'))
            
            # Print captured URLs
            print(f'\nCaptured {len(captured_urls)} responses')
            for u in captured_urls[-20:]:
                print(f'  [{u["status"]}] {u["ct"][:40]:40s} {u["size"]:>8s} {u["url"][:80]}')

        except Exception as e:
            import traceback
            print(f'Error: {e}')
            traceback.print_exc()
            try:
                page.screenshot(path=os.path.join(OUTPUT_DIR, '03-error.png'))
            except:
                pass
        finally:
            browser.close()

    # Final check
    pdf_path = os.path.join(OUTPUT_DIR, 'XSZS2604020200脱敏.pdf')
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 100000:
        print(f'\n🎉 SUCCESS: {pdf_path} ({os.path.getsize(pdf_path)} bytes)')
    else:
        print(f'\n❌ FAILED')

if __name__ == '__main__':
    main()

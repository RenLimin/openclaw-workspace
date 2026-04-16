#!/usr/bin/env python3
"""
Download PDF - use networkidle, longer waits, and check page properly.
"""
import json
import os
from playwright.sync_api import sync_playwright

STATE_FILE = '/Users/bangcle/.openclaw/workspace/training-reports/ella/oa-working-state.json'
OUTPUT_DIR = '/Users/bangcle/.openclaw/agents/ella/workspace/training-reports'

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

        try:
            # Step 1: Go to OA home with networkidle
            print('\n[1] Going to OA home...')
            resp = page.goto('https://oa.bangcle.com/', wait_until='networkidle', timeout=60000)
            print(f'Status: {resp.status}, URL: {page.url}')
            page.wait_for_timeout(5000)
            
            content = page.content()
            print(f'Content length: {len(content)}')
            print(f'First 500 chars: {content[:500]}')
            
            page.screenshot(path=os.path.join(OUTPUT_DIR, '01-oa-home.png'))
            
            # Check if logged in
            if '登录' in content[:2000] or 'login' in content[:1000].lower():
                print('❌ Login page!')
                return

            print('✅ Logged in')

            # Step 2: Navigate to contract detail
            print('\n[2] Going to contract detail...')
            contract_url = 'https://oa.bangcle.com/spa/cube/#/customPage?customid=179&mainTableDataId=14242'
            page.goto(contract_url, wait_until='networkidle', timeout=60000)
            page.wait_for_timeout(10000)
            
            page.screenshot(path=os.path.join(OUTPUT_DIR, '02-contract-page.png'))
            
            content = page.content()
            print(f'Content length: {len(content)}')
            
            # Check for key elements
            print(f'Has excelMainTable: {"excelMainTable" in content}')
            print(f'Has 脱敏: {"脱敏" in content}')
            print(f'Has download: {"icon-coms-download" in content}')
            print(f'Has wea-field-link: {"wea-field-link" in content}')
            
            if len(content) > 1000:
                print(f'First 500: {content[:500]}')
            else:
                print('⚠️ Page content is very short - page might not have loaded')
                # Try alternative navigation
                print('\n[2b] Trying alternative URL...')
                alt_url = 'https://oa.bangcle.com/formmode/data/CustomData.jsp?customid=179&mainTableDataId=14242'
                page.goto(alt_url, wait_until='networkidle', timeout=60000)
                page.wait_for_timeout(5000)
                page.screenshot(path=os.path.join(OUTPUT_DIR, '02b-alternate.png'))
                content = page.content()
                print(f'Alt content length: {len(content)}')
                print(f'Has 脱敏: {"脱敏" in content}')

            # Step 3: Find and click download
            print('\n[3] Looking for download elements...')
            
            # Try to find download icons
            download_icons = page.query_selector_all('.icon-coms-download')
            print(f'Download icons: {len(download_icons)}')
            
            # Try to find file links
            file_links = page.query_selector_all('a.wea-field-link')
            print(f'File links: {len(file_links)}')
            for link in file_links:
                title = link.get_attribute('title')
                print(f'  File: {title}')
            
            # If nothing found, try scrolling
            if not download_icons and not file_links:
                print('Scrolling to find elements...')
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                page.wait_for_timeout(3000)
                page.screenshot(path=os.path.join(OUTPUT_DIR, '03-scrolled.png'))
                
                download_icons = page.query_selector_all('.icon-coms-download')
                file_links = page.query_selector_all('a.wea-field-link')
                print(f'After scroll - Icons: {len(download_icons)}, Links: {len(file_links)}')
            
            # Click download
            if download_icons:
                print('\n[4] Clicking download icon...')
                with page.expect_download(timeout=20000) as dl_info:
                    download_icons[0].click()
                download = dl_info.value
                save_path = os.path.join(OUTPUT_DIR, download.suggested_filename() or 'XSZS2604020200脱敏.pdf')
                download.save_as(save_path)
                size = os.path.getsize(save_path)
                print(f'Saved: {save_path} ({size} bytes)')
                with open(save_path, 'rb') as f:
                    header = f.read(10)
                if header[:4] == b'%PDF':
                    print('✅ Confirmed PDF!')
                    downloaded_path = save_path
                else:
                    print(f'⚠️ Header: {header}')
                    with open(save_path, 'r', errors='replace') as f:
                        print(f'Content: {f.read(200)}')
            elif file_links:
                print('\n[4] Clicking file link...')
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
                            print('✅ Confirmed PDF!')
                            downloaded_path = save_path
                        break
            else:
                print('❌ No download elements found')
                # Print all links for debugging
                all_links = page.query_selector_all('a')
                print(f'Total links: {len(all_links)}')
                for link in all_links[:20]:
                    href = link.get_attribute('href')
                    text = (link.inner_text() or '').strip()[:40]
                    print(f'  [{text}] {href[:80] if href else "(no href)"}')

            page.screenshot(path=os.path.join(OUTPUT_DIR, '04-final.png'))

        except Exception as e:
            import traceback
            traceback.print_exc()
            try:
                page.screenshot(path=os.path.join(OUTPUT_DIR, '04-error.png'))
            except:
                pass
        finally:
            browser.close()

    # Final
    pdf_path = os.path.join(OUTPUT_DIR, 'XSZS2604020200脱敏.pdf')
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 100000:
        print(f'\n🎉 SUCCESS: {pdf_path} ({os.path.getsize(pdf_path)} bytes)')
    else:
        print(f'\n❌ FAILED')

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Download PDF - properly wait for SPA to render, use correct selectors.
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
            # Step 1: Go to OA home
            print('\n[1] Going to OA home...')
            resp = page.goto('https://oa.bangcle.com/', wait_until='networkidle', timeout=60000)
            print(f'Status: {resp.status}, URL: {page.url}')
            page.wait_for_timeout(5000)
            
            content = page.content()
            print(f'Content length: {len(content)}')
            
            # Check if we're on login page
            if '登录' in content[:2000] or 'login' in page.url.lower():
                print('❌ Not logged in!')
                page.screenshot(path=os.path.join(OUTPUT_DIR, '01-login.png'))
                return
            
            page.screenshot(path=os.path.join(OUTPUT_DIR, '01-oa-home.png'))
            print('✅ Seem logged in')

            # Step 2: Navigate to contract detail SPA page
            print('\n[2] Navigating to contract detail...')
            contract_url = 'https://oa.bangcle.com/spa/cube/#/customPage?customid=179&mainTableDataId=14242'
            page.goto(contract_url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for SPA to render - look for the main table
            print('Waiting for SPA to render...')
            try:
                page.wait_for_selector('table.excelMainTable', timeout=30000)
                print('✅ Main table found!')
            except:
                print('⚠️ Main table not found, checking page...')
                page.wait_for_timeout(10000)
            
            page.screenshot(path=os.path.join(OUTPUT_DIR, '02-contract-page.png'))
            print(f'Page URL: {page.url}')
            
            content = page.content()
            print(f'Content length: {len(content)}')
            
            # Check for key content
            has_脱敏 = '脱敏' in content
            has_download = 'icon-coms-download' in content
            has_link = 'wea-field-link' in content
            print(f'Has 脱敏: {has_脱敏}, Has download icon: {has_download}, Has file link: {has_link}')

            if not has_脱敏 and not has_download and not has_link:
                print('❌ Page content not as expected')
                print(f'First 1000 chars: {content[:1000]}')
                # Maybe page needs more time or scroll
                print('Trying to scroll and wait more...')
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                page.wait_for_timeout(5000)
                page.screenshot(path=os.path.join(OUTPUT_DIR, '02-scrolled.png'))
                content = page.content()
                has_脱敏 = '脱敏' in content
                has_download = 'icon-coms-download' in content
                has_link = 'wea-field-link' in content
                print(f'After scroll - Has 脱敏: {has_脱敏}, Has download: {has_download}, Has link: {has_link}')

            # Step 3: Find download elements
            print('\n[3] Finding download elements...')
            
            download_icons = page.query_selector_all('.icon-coms-download')
            print(f'Download icons: {len(download_icons)}')
            
            file_links = page.query_selector_all('a.wea-field-link')
            print(f'File links: {len(file_links)}')
            for link in file_links:
                title = link.get_attribute('title')
                text = link.inner_text()
                print(f'  Link: title="{title}", text="{text}"')

            # Click download
            if download_icons:
                print('\n[4] Clicking first download icon...')
                with page.expect_download(timeout=20000) as dl_info:
                    download_icons[0].click()
                download = dl_info.value
                filename = download.suggested_filename()
                print(f'Download filename: {filename}')
                save_path = os.path.join(OUTPUT_DIR, filename or 'XSZS2604020200脱敏.pdf')
                download.save_as(save_path)
                size = os.path.getsize(save_path)
                print(f'Saved: {save_path} ({size} bytes)')
                # Verify
                with open(save_path, 'rb') as f:
                    header = f.read(10)
                if header[:4] == b'%PDF':
                    print('✅ PDF confirmed!')
                    downloaded_path = save_path
                else:
                    print(f'⚠️ Not PDF, header: {header}')
                    with open(save_path, 'r', errors='replace') as f:
                        print(f'Content: {f.read(300)}')
            elif file_links:
                print('\n[4] Clicking file link...')
                for link in file_links:
                    title = link.get_attribute('title')
                    if title and '.pdf' in title:
                        print(f'Clicking: {title}')
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
                            print('✅ PDF confirmed!')
                            downloaded_path = save_path
                        break
            else:
                print('❌ No download elements found')
                # Debug: list all interactive elements
                buttons = page.query_selector_all('button, a, i[class*="download"]')
                print(f'Total interactive: {len(buttons)}')
                for el in buttons[:20]:
                    tag = el.evaluate('el => el.tagName.toLowerCase()')
                    cls = el.get_attribute('class') or ''
                    text = (el.inner_text() or '').strip()[:30]
                    print(f'  <{tag}> class="{cls[:50]}" text="{text}"')

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

    # Final check
    pdf_path = os.path.join(OUTPUT_DIR, 'XSZS2604020200脱敏.pdf')
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 100000:
        print(f'\n🎉 SUCCESS: {pdf_path} ({os.path.getsize(pdf_path)} bytes)')
    else:
        print(f'\n❌ FAILED - PDF not found or too small')
        # List relevant files
        for f in sorted(os.listdir(OUTPUT_DIR)):
            if 'XSZS2604020200' in f:
                print(f'  {f}: {os.path.getsize(os.path.join(OUTPUT_DIR, f))} bytes')

if __name__ == '__main__':
    main()

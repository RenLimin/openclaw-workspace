#!/usr/bin/env python3
"""
Download PDF by navigating OA and clicking download button.
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
    for c in state['cookies']:
        print(f'  {c["name"]}: domain={c.get("domain","")}, expires={c.get("expires","")}')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(
            storage_state=STATE_FILE,
            accept_downloads=True,
            viewport={'width': 1440, 'height': 900},
        )
        page = context.new_page()
        downloaded_path = None

        try:
            # Go to OA home first
            print('\n[1] Navigating to OA home...')
            resp = page.goto('https://oa.bangcle.com/', wait_until='domcontentloaded', timeout=30000)
            print(f'Status: {resp.status}, URL: {page.url}')
            page.wait_for_timeout(3000)
            page.screenshot(path=os.path.join(OUTPUT_DIR, '01-oa-home.png'))

            # Check if we're logged in
            page_content = page.content()
            if '登录' in page_content[:2000] or 'login' in page.url.lower():
                print('❌ Not logged in - redirect to login page')
                # Take screenshot for debugging
                page.screenshot(path=os.path.join(OUTPUT_DIR, '01-login-redirect.png'))
                return

            print('✅ Seem logged in')

            # Navigate to contract detail
            print('\n[2] Navigating to contract detail...')
            contract_url = 'https://oa.bangcle.com/spa/cube/#/customPage?customid=179&mainTableDataId=14242'
            page.goto(contract_url, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(8000)
            page.screenshot(path=os.path.join(OUTPUT_DIR, '02-contract-page.png'))
            print(f'Page URL: {page.url}')

            title = page.title()
            print(f'Page title: {title}')

            # Wait for content to load
            page.wait_for_selector('table.excelMainTable', timeout=15000)
            print('✅ Main table loaded')

            # Scroll down to find the attachment section
            print('\n[3] Scrolling to find attachment section...')
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            page.wait_for_timeout(2000)
            page.screenshot(path=os.path.join(OUTPUT_DIR, '03-scrolled.png'))

            # Try to find download icon
            download_icons = page.query_selector_all('.icon-coms-download')
            print(f'Found {len(download_icons)} download icons')

            # Also try to find file links
            file_links = page.query_selector_all('a.wea-field-link')
            print(f'Found {len(file_links)} file links')
            for i, link in enumerate(file_links):
                title_attr = link.get_attribute('title')
                href = link.get_attribute('href')
                text = link.inner_text()
                print(f'  Link {i}: title="{title_attr}", href="{href}", text="{text}"')

            # Try downloading via clicking the download icon
            if download_icons:
                print('\n[4] Clicking first download icon...')
                # Set up download listener
                with page.expect_download(timeout=20000) as dl_info:
                    download_icons[0].click()
                    print('Clicked download icon')
                download = dl_info.value
                suggested = download.suggested_filename()
                print(f'Download: {suggested}')
                save_path = os.path.join(OUTPUT_DIR, suggested or 'XSZS2604020200脱敏.pdf')
                download.save_as(save_path)
                size = os.path.getsize(save_path)
                print(f'✅ Saved: {save_path} ({size} bytes)')
                downloaded_path = save_path
            elif file_links:
                # Try clicking the file link
                for link in file_links:
                    title_attr = link.get_attribute('title')
                    if title_attr and '.pdf' in title_attr:
                        print(f'\n[4] Clicking file link: {title_attr}')
                        with page.expect_download(timeout=20000) as dl_info:
                            link.click()
                        download = dl_info.value
                        save_path = os.path.join(OUTPUT_DIR, download.suggested_filename() or 'XSZS2604020200脱敏.pdf')
                        download.save_as(save_path)
                        size = os.path.getsize(save_path)
                        print(f'✅ Saved: {save_path} ({size} bytes)')
                        downloaded_path = save_path
                        break
            else:
                print('❌ No download icons or file links found')

            # Check if it's actually a PDF
            if downloaded_path:
                with open(downloaded_path, 'rb') as f:
                    header = f.read(10)
                if header[:4] == b'%PDF':
                    print(f'✅ Confirmed PDF: {downloaded_path}')
                else:
                    print(f'❌ Not a PDF (header: {header})')
                    # It might be an HTML redirect
                    with open(downloaded_path, 'r', errors='replace') as f:
                        content = f.read(500)
                    print(f'Content preview: {content[:200]}')

            page.screenshot(path=os.path.join(OUTPUT_DIR, '04-final.png'))

        except Exception as e:
            print(f'Error: {e}')
            try:
                page.screenshot(path=os.path.join(OUTPUT_DIR, '04-error.png'))
            except:
                pass
        finally:
            browser.close()

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Download PDF from OA using Playwright with stored cookies.
"""
import json
import os
import time
from playwright.sync_api import sync_playwright

STATE_FILE = '/Users/bangcle/.openclaw/workspace/training-reports/ella/oa-working-state.json'
OUTPUT_DIR = '/Users/bangcle/.openclaw/agents/ella/workspace/training-reports'
FILE_ID = '205115'
PDF_NAME = 'XSZS2604020200脱敏.pdf'

def main():
    if not os.path.exists(STATE_FILE):
        print(f'❌ State file not found: {STATE_FILE}')
        return

    with open(STATE_FILE) as f:
        storage_state = json.load(f)
    
    print(f'Loaded state with {len(storage_state.get("cookies", []))} cookies')

    downloaded_path = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(
            storage_state=STATE_FILE,
            accept_downloads=True,
            viewport={'width': 1440, 'height': 900},
        )
        page = context.new_page()
        
        # Intercept all responses to catch PDF downloads
        def handle_response(response):
            nonlocal downloaded_path
            url = response.url
            ct = response.headers.get('content-type', '')
            if 'pdf' in ct or 'octet-stream' in ct or ('download' in url.lower() and response.status == 200):
                print(f'[Intercept] URL: {url[:120]}...')
                print(f'[Intercept] Content-Type: {ct}, Status: {response.status}')
                try:
                    body = response.body()
                    print(f'[Intercept] Body size: {len(body)} bytes')
                    if len(body) > 1000:
                        pdf_path = os.path.join(OUTPUT_DIR, PDF_NAME)
                        with open(pdf_path, 'wb') as f:
                            f.write(body)
                        print(f'✅ PDF saved via intercept: {pdf_path} ({len(body)} bytes)')
                        downloaded_path = pdf_path
                except Exception as e:
                    print(f'[Intercept] Could not read body: {e}')

        page.on('response', handle_response)

        try:
            # Method 1: Direct API download
            print('\n[Method 1] Direct API download...')
            api_url = f'https://oa.bangcle.com/weaver/weaver.file.FileDownload?fileid={FILE_ID}&isFromPdfShow=1'
            try:
                resp = page.request.get(api_url)
                print(f'API Status: {resp.status}, Content-Type: {resp.headers.get("content-type", "")}')
                if resp.status == 200:
                    body = resp.body()
                    ct = resp.headers.get('content-type', '')
                    if 'pdf' in ct or 'octet-stream' in ct or len(body) > 1000:
                        pdf_path = os.path.join(OUTPUT_DIR, PDF_NAME)
                        with open(pdf_path, 'wb') as f:
                            f.write(body)
                        print(f'✅ PDF saved via API: {pdf_path} ({len(body)} bytes)')
                        downloaded_path = pdf_path
                    else:
                        print(f'API returned {len(body)} bytes, CT={ct}')
                        # Save response for debugging
                        debug_path = os.path.join(OUTPUT_DIR, 'api-response-debug.bin')
                        with open(debug_path, 'wb') as f:
                            f.write(body)
                        print(f'Saved debug response to {debug_path}')
            except Exception as e:
                print(f'API download failed: {e}')

            if downloaded_path and os.path.getsize(downloaded_path) > 1000:
                print(f'\n✅ PDF downloaded successfully: {downloaded_path}')
            else:
                # Method 2: Navigate to page and click download
                print('\n[Method 2] Navigate to page and click download...')
                contract_url = 'https://oa.bangcle.com/spa/cube/#/customPage?customid=179&mainTableDataId=14242'
                print(f'Navigating to: {contract_url}')
                page.goto(contract_url, wait_until='domcontentloaded', timeout=30000)
                page.wait_for_timeout(5000)
                
                page.screenshot(path=os.path.join(OUTPUT_DIR, '01-contract-page.png'))
                print(f'Page URL: {page.url}')
                print(f'Page title: {page.title()}')

                # Look for download icons
                download_icons = page.query_selector_all('.icon-coms-download')
                print(f'Found {len(download_icons)} download icons')

                if download_icons and not downloaded_path:
                    # Set up download listener
                    with page.expect_download(timeout=15000) as dl_info:
                        download_icons[0].click()
                    download = dl_info.value
                    save_path = os.path.join(OUTPUT_DIR, download.suggested_filename() or PDF_NAME)
                    download.save_as(save_path)
                    print(f'✅ PDF saved via click: {save_path} ({os.path.getsize(save_path)} bytes)')
                    downloaded_path = save_path
                else:
                    # Try file links
                    file_links = page.query_selector_all('a.wea-field-link')
                    print(f'Found {len(file_links)} file links')
                    for link in file_links:
                        title = link.get_attribute('title')
                        if title and '.pdf' in title:
                            print(f'Clicking file link: {title}')
                            with page.expect_download(timeout=15000) as dl_info:
                                link.click()
                            download = dl_info.value
                            save_path = os.path.join(OUTPUT_DIR, download.suggested_filename() or PDF_NAME)
                            download.save_as(save_path)
                            print(f'✅ PDF saved via link: {save_path} ({os.path.getsize(save_path)} bytes)')
                            downloaded_path = save_path
                            break

            if not downloaded_path or not os.path.exists(downloaded_path) or os.path.getsize(downloaded_path) < 1000:
                # Method 3: Try alternative API patterns
                print('\n[Method 3] Alternative API patterns...')
                alt_urls = [
                    f'https://oa.bangcle.com/api/ec/dev/file/download?fileId={FILE_ID}',
                    f'https://oa.bangcle.com/api/ecology/file/download?fileId={FILE_ID}',
                    f'https://oa.bangcle.com/weaver/FileDownload.jsp?fileid={FILE_ID}',
                ]
                for alt_url in alt_urls:
                    try:
                        resp = page.request.get(alt_url)
                        ct = resp.headers.get('content-type', '')
                        if resp.status == 200 and ('pdf' in ct or 'octet-stream' in ct):
                            body = resp.body()
                            if len(body) > 1000:
                                pdf_path = os.path.join(OUTPUT_DIR, PDF_NAME)
                                with open(pdf_path, 'wb') as f:
                                    f.write(body)
                                print(f'✅ PDF saved via alt API: {pdf_path} ({len(body)} bytes)')
                                downloaded_path = pdf_path
                                break
                        print(f'Alt URL {alt_url[:80]}... -> Status {resp.status}, CT: {ct}')
                    except Exception as e:
                        print(f'Alt URL failed: {e}')

            page.screenshot(path=os.path.join(OUTPUT_DIR, '02-final-state.png'))

        except Exception as e:
            print(f'Error: {e}')
            try:
                page.screenshot(path=os.path.join(OUTPUT_DIR, '02-error-state.png'))
            except:
                pass
        finally:
            browser.close()

    # Final result
    pdf_path = os.path.join(OUTPUT_DIR, PDF_NAME)
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
        print(f'\n🎉 SUCCESS: PDF saved to {pdf_path} ({os.path.getsize(pdf_path)} bytes)')
    else:
        print(f'\n❌ FAILED: PDF not found or too small')
        # List what we have
        for f in os.listdir(OUTPUT_DIR):
            if 'XSZS2604020200' in f or 'debug' in f:
                fp = os.path.join(OUTPUT_DIR, f)
                print(f'  {f}: {os.path.getsize(fp)} bytes')

if __name__ == '__main__':
    main()

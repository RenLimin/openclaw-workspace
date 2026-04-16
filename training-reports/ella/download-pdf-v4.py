#!/usr/bin/env python3
"""
Download PDF from OA using httpx with stored cookies - no browser needed.
"""
import json
import os
import re
import httpx
import asyncio

STATE_FILE = '/Users/bangcle/.openclaw/workspace/training-reports/ella/oa-working-state.json'
OUTPUT_DIR = '/Users/bangcle/.openclaw/agents/ella/workspace/training-reports'
FILE_ID = '205115'
PDF_NAME = 'XSZS2604020200脱敏.pdf'

def main():
    with open(STATE_FILE) as f:
        state = json.load(f)
    
    # Build cookies dict
    cookies = {}
    for c in state.get('cookies', []):
        cookies[c['name']] = c['value']
    
    print(f'Using {len(cookies)} cookies')
    for k, v in cookies.items():
        print(f'  {k}: {v[:50]}...')
    
    # Build cookie header for manual setting
    cookie_str = '; '.join(f'{k}={v}' for k, v in cookies.items())
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://oa.bangcle.com/',
        'Cookie': cookie_str,
    }
    
    # Try various download URL patterns
    urls = [
        # Weaver OA standard patterns
        f'https://oa.bangcle.com/weaver/weaver.file.FileDownload?fileid={FILE_ID}&isFromPdfShow=1',
        f'https://oa.bangcle.com/weaver/FileDownload.jsp?fileid={FILE_ID}',
        f'https://oa.bangcle.com/weaver/weaver.file.FileDownload?fileid={FILE_ID}',
        f'https://oa.bangcle.com/api/ec/dev/file/download?fileId={FILE_ID}',
        f'https://oa.bangcle.com/api/ec/dev/attach/download?fileId={FILE_ID}',
        f'https://oa.bangcle.com/api/ec/dev/file/getFile?fileId={FILE_ID}',
        f'https://oa.bangcle.com/cloudstore/download?fileId={FILE_ID}',
        # Cube/SPA patterns
        f'https://oa.bangcle.com/spa/cube/api/file/download?fileId={FILE_ID}',
        f'https://oa.bangcle.com/spa/cube/api/attach/download?fileId={FILE_ID}',
        # With billId (mainTableDataId=14242)
        f'https://oa.bangcle.com/api/ec/dev/attach/getAttachByFormData?formId=112&billId=14242',
        f'https://oa.bangcle.com/api/ec/dev/formmode/getAttachByFormData?formId=-249&billId=14242',
    ]
    
    client = httpx.Client(follow_redirects=True, timeout=30, verify=False)
    
    for url in urls:
        print(f'\n[>] GET {url[:100]}...')
        try:
            resp = client.get(url, headers=headers)
            ct = resp.headers.get('content-type', '')
            content_length = resp.headers.get('content-length', '?')
            print(f'  Status: {resp.status}, CT: {ct[:80]}, Len: {content_length}, Size: {len(resp.content)}')
            
            # Check if it's a PDF
            if 'pdf' in ct.lower() or 'octet-stream' in ct.lower() or 'application' in ct.lower():
                if len(resp.content) > 10000:  # PDF should be > 10KB
                    pdf_path = os.path.join(OUTPUT_DIR, PDF_NAME)
                    with open(pdf_path, 'wb') as f:
                        f.write(resp.content)
                    print(f'  ✅ PDF SAVED: {pdf_path} ({len(resp.content)} bytes)')
                    # Verify it's actually a PDF
                    if resp.content[:4] == b'%PDF':
                        print(f'  ✅ Confirmed PDF header')
                    else:
                        print(f'  ⚠️ Not a PDF header: {resp.content[:20]}')
                    client.close()
                    return
                else:
                    print(f'  ⚠️ PDF-like CT but only {len(resp.content)} bytes')
            
            # Check if HTML contains a redirect or iframe
            if 'html' in ct.lower():
                text = resp.text[:500]
                # Look for iframe src or JS redirect
                iframe = re.search(r'iframe[^>]+src=["\']([^"\']+)["\']', text)
                if iframe:
                    print(f'  → Iframe found: {iframe.group(1)[:100]}')
                js_redirect = re.search(r'window\.location[^=]*=\s*["\']([^"\']+)["\']', text)
                if js_redirect:
                    print(f'  → JS redirect: {js_redirect.group(1)[:100]}')
                if '登录' in text[:200] or 'login' in text[:200].lower():
                    print(f'  ❌ Login page detected')
                elif len(resp.content) < 500:
                    print(f'  → Small HTML response: {text[:100]}')
            
            # Check for JSON response
            if 'json' in ct.lower():
                try:
                    data = resp.json()
                    print(f'  JSON: {json.dumps(data, ensure_ascii=False)[:300]}')
                    # Look for file URLs in JSON
                    def find_urls(obj, path=''):
                        if isinstance(obj, dict):
                            for k, v in obj.items():
                                if isinstance(v, str) and ('http' in v or 'download' in v.lower() or '.pdf' in v.lower()):
                                    print(f'  → URL in JSON: {k}={v[:100]}')
                                find_urls(v, f'{path}.{k}')
                        elif isinstance(obj, list):
                            for i, v in enumerate(obj):
                                find_urls(v, f'{path}[{i}]')
                    find_urls(data)
                except:
                    pass
            
            # Save debug for first few URLs
            if 'html' in ct.lower() and len(resp.content) > 100:
                debug_path = os.path.join(OUTPUT_DIR, f'debug-response-{FILE_ID}.html')
                with open(debug_path, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(resp.text)
                print(f'  Saved debug HTML to {debug_path}')
                
        except Exception as e:
            print(f'  Error: {e}')
    
    client.close()
    print('\n❌ No PDF found via any URL pattern')

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
直接调用 /apps/jumpSystem API 获取 OA URL
"""

import asyncio
import json
import requests

# Get cookie and token from existing login
import subprocess
result = subprocess.run(['/Library/Frameworks/Python.framework/Versions/3.10/bin/python3', '-c', '''
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        # Login
        await page.goto("https://iam.bangcle.com/", wait_until="networkidle", timeout=30000)
        import time
        time.sleep(3)
        
        if "home" not in page.url and "index" not in page.url:
            inputs = await page.query_selector_all("input")
            text_inputs = [i for i in inputs if await i.get_attribute("type") in ["text","password"] and await i.is_visible()]
            if len(text_inputs) >= 2:
                await text_inputs[0].fill("limin.ren")
                await text_inputs[1].fill("June-123")
                btn = page.get_by_role("button", name="登录")
                if await btn.is_visible():
                    await btn.click()
                else:
                    await text_inputs[1].press("Enter")
                await asyncio.sleep(10)
        
        await page.goto("https://iam.bangcle.com/#/home/index", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(8)
        
        # Get token
        state = await page.evaluate("() => localStorage.getItem('GlobalState')")
        print(f"TOKEN:{state}")
        
        # Get cookies
        cookies = await context.cookies()
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        print(f"COOKIES:{cookie_str}")
        
        await browser.close()

asyncio.run(main())
'''], capture_output=True, text=True, timeout=60)

print("Login output:")
print(result.stdout[:500])

# Parse token and cookies
token = None
cookies_str = None
for line in result.stdout.split('\n'):
    if line.startswith('TOKEN:'):
        token = line.split(':', 1)[1]
    elif line.startswith('COOKIES:'):
        cookies_str = line.split(':', 1)[1]

print(f"\nToken: {token[:50] if token else 'NOT FOUND'}...")
print(f"Cookies: {cookies_str[:50] if cookies_str else 'NOT FOUND'}...")

if not token:
    print("Failed to get token")
    exit(1)

# Now try to call the jumpSystem API
import requests
session = requests.Session()

# Set cookies
if cookies_str:
    for cookie in cookies_str.split('; '):
        name, value = cookie.split('=', 1)
        session.cookies.set(name, value, domain='.bangcle.com')

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Referer': 'https://iam.bangcle.com/'
}

# Try to get the app list first
print("\nStep 1: 获取应用列表...")
resp = session.post('https://iam.bangcle.com/apps/getPermissionApps', 
                     json={'userId': '1313'},
                     headers={**headers, 'noLoading': 'true'})
print(f"  状态码: {resp.status_code}")
if resp.status_code == 200:
    apps = resp.json()
    print(f"  应用数量: {len(apps.get('data', []))}")
    for app in apps.get('data', []):
        print(f"    - {app.get('systemname')}: id={app.get('id')}, systemkey={app.get('systemkey')}, link={app.get('systemlink')}, domain={app.get('domain')}")
        
        # Find OA
        if 'OA' in app.get('systemname', '') or '协同' in app.get('systemname', ''):
            oa_id = app.get('id')
            print(f"\n  ✅ 找到 OA! ID={oa_id}")
            
            # Call jumpSystem
            print(f"\nStep 2: 调用 jumpSystem API...")
            resp2 = session.get(f'https://iam.bangcle.com/apps/jumpSystem', 
                               params={'appid': oa_id},
                               headers=headers)
            print(f"  状态码: {resp2.status_code}")
            print(f"  响应: {resp2.text[:500]}")
            
            # Try to follow redirect
            if resp2.status_code in [301, 302]:
                redirect_url = resp2.headers.get('Location', '')
                print(f"  重定向: {redirect_url}")

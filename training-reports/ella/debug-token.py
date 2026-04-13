#!/usr/bin/env python3
"""
直接使用 page.evaluate 调用 jumpSystem - 调试 token
"""

import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        out = '/Users/bangcle/.openclaw/workspace/training-reports/ella/'
        
        print("=" * 60)
        print("调试 Token 并调用 jumpSystem")
        print("=" * 60)
        
        # Login
        await page.goto('https://iam.bangcle.com/', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(3)
        
        if 'home' not in page.url and 'index' not in page.url:
            inputs = await page.query_selector_all('input')
            text_inputs = [i for i in inputs 
                          if await i.get_attribute('type') in ['text','password','email','tel'] 
                          and await i.is_visible()]
            if len(text_inputs) >= 2:
                await text_inputs[0].fill('limin.ren')
                await text_inputs[1].fill('June-123')
                btn = page.get_by_role("button", name="登录")
                if await btn.is_visible():
                    await btn.click()
                else:
                    await text_inputs[1].press('Enter')
                await asyncio.sleep(10)
        
        await page.goto('https://iam.bangcle.com/#/home/index', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(8)
        
        # Debug token
        print("\nStep 1: 调试 Token...")
        
        debug = await page.evaluate("""() => {
            const raw = localStorage.getItem('GlobalState');
            const state = raw ? JSON.parse(raw) : null;
            const token = state?.token || '';
            
            return {
                hasRaw: !!raw,
                rawLength: raw ? raw.length : 0,
                hasToken: !!token,
                tokenLength: token.length,
                tokenStart: token.substring(0, 30),
                userId: state?.userInfo?.userid || 'N/A'
            };
        }""")
        print(f"  调试信息: {debug}")
        
        # Step 2: Direct fetch test
        print("\nStep 2: 直接 fetch 测试...")
        
        result = await page.evaluate("""async () => {
            const raw = localStorage.getItem('GlobalState');
            const state = JSON.parse(raw);
            const token = state.token;
            
            console.log('Token length:', token.length);
            console.log('Token start:', token.substring(0, 20));
            
            const url = '/api/application/apps/jumpSystem?appid=9';
            console.log('URL:', url);
            console.log('Auth header:', 'Bearer ' + token.substring(0, 20) + '...');
            
            try {
                const resp = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'Authorization': 'Bearer ' + token
                    }
                });
                const text = await resp.text();
                return {
                    status: resp.status,
                    text: text.substring(0, 200),
                    headers: Object.fromEntries(resp.headers.entries())
                };
            } catch(e) {
                return {error: e.message};
            }
        }""")
        print(f"  结果: {result}")
        
        # Step 3: Try with XMLHttpRequest
        print("\nStep 3: XHR 测试...")
        
        xhr_result = await page.evaluate("""() => {
            return new Promise((resolve) => {
                const raw = localStorage.getItem('GlobalState');
                const state = JSON.parse(raw);
                const token = state.token;
                
                const xhr = new XMLHttpRequest();
                xhr.open('GET', '/api/application/apps/jumpSystem?appid=9', true);
                xhr.setRequestHeader('Authorization', 'Bearer ' + token);
                xhr.onload = function() {
                    resolve({
                        status: xhr.status,
                        text: xhr.responseText.substring(0, 200)
                    });
                };
                xhr.onerror = function() {
                    resolve({error: 'XHR error'});
                };
                xhr.send();
            });
        }""")
        print(f"  XHR 结果: {xhr_result}")
        
        await browser.close()

asyncio.run(main())

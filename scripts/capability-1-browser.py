#!/usr/bin/env python3
"""
能力 1: 浏览器自动化测试
测试 Playwright 无头模式的基本能力
"""
import os
import sys
from playwright.sync_api import sync_playwright

def test_headless_browse(url, screenshot_path=None):
    """测试 1.1: 无头模式访问网页"""
    print(f"🌐 访问: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        title = page.title()
        content = page.inner_text("body")[:500]
        print(f"  标题: {title}")
        print(f"  内容预览: {content[:200]}...")
        if screenshot_path:
            page.screenshot(path=screenshot_path)
            print(f"  截图: {screenshot_path}")
        browser.close()
        return {"title": title, "content": content[:200]}

def test_content_extraction():
    """测试 1.2: 网页内容提取"""
    print("\n📄 提取网页结构化内容...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://httpbin.org/html", wait_until="domcontentloaded", timeout=10000)
        # 提取结构化信息
        headings = page.query_selector_all("h1, h2, h3")
        links = page.query_selector_all("a")
        print(f"  标题数量: {len(headings)}")
        print(f"  链接数量: {len(links)}")
        browser.close()
        return {"headings": len(headings), "links": len(links)}

def test_screenshot():
    """测试 1.3: 截图功能"""
    print("\n📸 截图测试...")
    os.makedirs("/tmp/browser-tests", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://httpbin.org/html", wait_until="domcontentloaded", timeout=10000)
        path = "/tmp/browser-tests/screenshot-test.png"
        page.screenshot(path=path, full_page=True)
        size = os.path.getsize(path)
        print(f"  截图路径: {path}")
        print(f"  文件大小: {size:,} bytes")
        browser.close()
        return path

def main():
    print("=" * 50)
    print("能力 1: 浏览器自动化测试")
    print("=" * 50)
    
    results = {}
    try:
        r1 = test_headless_browse("https://httpbin.org/html", "/tmp/browser-tests/homepage.png")
        results["test_1_1_headless"] = "✅ 通过"
    except Exception as e:
        results["test_1_1_headless"] = f"❌ 失败: {e}"
    
    try:
        r2 = test_content_extraction()
        results["test_1_2_extraction"] = "✅ 通过"
    except Exception as e:
        results["test_1_2_extraction"] = f"❌ 失败: {e}"
    
    try:
        r3 = test_screenshot()
        results["test_1_3_screenshot"] = "✅ 通过"
    except Exception as e:
        results["test_1_3_screenshot"] = f"❌ 失败: {e}"
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    print("=" * 50)
    
    return all("✅" in v for v in results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

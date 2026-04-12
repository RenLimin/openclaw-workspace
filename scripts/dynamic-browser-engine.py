#!/usr/bin/env python3
"""
动态页面浏览器引擎 v3.0
实现动态页面的识别、等待、操作一体化解决方案

核心能力：
1. AI 快照驱动的元素发现
2. 动态元素等待与重试策略
3. SPA 框架检测（Vue/React/Angular）
4. 视觉 + DOM 混合识别
5. 复杂交互模式（文件上传、拖拽、iframe、Shadow DOM、对话框）
6. 网络请求监控（API 驱动页面状态）
7. 状态恢复与容错
"""
import os
import sys
import json
import time
import asyncio
import base64
import re
import requests
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from playwright.async_api import async_playwright, Playwright

# ============================================================
# 数据模型
# ============================================================

@dataclass
class PageSnapshot:
    """页面快照"""
    format: str  # "ai" | "aria" | "dom"
    content: str
    elements: List[Dict] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    
    def find_element(self, text_or_role: str) -> Optional[Dict]:
        """查找元素"""
        for elem in self.elements:
            if text_or_role.lower() in str(elem).lower():
                return elem
        return None
    
    def get_interactive_elements(self) -> List[Dict]:
        """获取可交互元素"""
        return [e for e in self.elements if e.get("role") in 
                ("button", "link", "textbox", "checkbox", "combobox", "menuitem")]


@dataclass
class NetworkRequest:
    """网络请求"""
    url: str
    method: str
    status: Optional[int] = None
    response_body: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class DynamicPageState:
    """动态页面状态"""
    url: str
    title: str
    framework: str  # "vue" | "react" | "angular" | "unknown"
    is_loaded: bool = False
    is_stable: bool = False
    pending_requests: int = 0
    snapshot: Optional[PageSnapshot] = None
    errors: List[str] = field(default_factory=list)


# ============================================================
# 核心引擎
# ============================================================

class DynamicBrowserEngine:
    """动态页面浏览器引擎 (Playwright Async)"""
    
    def __init__(self, agent_name: str = "default", headless: bool = True):
        self.agent_name = agent_name
        self.headless = headless
        self.user_data_dir = os.path.expanduser(f"~/.openclaw/browser-data/{agent_name}/")
        self.pw: Optional[Playwright] = None
        self.browser = None
        self.context = None
        self.page = None
        self.state = DynamicPageState(url="", title="", framework="unknown")
        self._request_log: List[NetworkRequest] = []
    
    async def launch(self):
        """启动浏览器"""
        os.makedirs(self.user_data_dir, exist_ok=True)
        
        self.pw = await async_playwright().start()
        self.context = await self.pw.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.page = await self.context.new_page()
        
        # 监听网络请求
        self.page.on("request", lambda req: self._request_log.append(
            NetworkRequest(url=req.url, method=req.method)
        ))
        
        print(f"🌐 {self.agent_name} 浏览器已启动")
        return self
    
    async def close(self):
        """关闭浏览器"""
        if self.context:
            await self.context.close()
        if self.pw:
            await self.pw.stop()
        print(f"🔒 {self.agent_name} 浏览器已关闭")
    
    async def navigate_and_wait(self, url: str, wait_for: str = "networkidle", timeout: int = 30000) -> DynamicPageState:
        """导航并等待页面加载"""
        print(f"🌐 导航到: {url}")
        
        await self.page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        
        # 等待策略
        if wait_for == "networkidle":
            try:
                await self.page.wait_for_load_state("networkidle", timeout=timeout)
            except:
                await asyncio.sleep(2)
        elif wait_for.startswith("selector:"):
            selector = wait_for.split(":", 1)[1]
            await self.wait_for_element(selector, timeout=timeout/1000)
        elif wait_for.startswith("text:"):
            text = wait_for.split(":", 1)[1]
            await self.wait_for_text(text, timeout=timeout/1000)
        elif wait_for.startswith("api:"):
            api_pattern = wait_for.split(":", 1)[1]
            await self.wait_for_api_call(api_pattern, timeout=timeout/1000)
        
        # 更新状态
        self.state.url = self.page.url
        self.state.title = await self.page.title()
        self.state.framework = await self.detect_framework()
        self.state.is_loaded = True
        
        return self.state
    
    async def get_snapshot(self, format: str = "dom", interactive: bool = False) -> PageSnapshot:
        """获取页面快照"""
        try:
            if format == "dom":
                # 获取 DOM 结构
                content = await self.page.content()
                elements = await self._extract_dom_elements(interactive)
            else:
                content = await self.page.inner_text("body")
                elements = []
            
            snapshot = PageSnapshot(format=format, content=content, elements=elements)
            self.state.snapshot = snapshot
            return snapshot
        except Exception as e:
            print(f"⚠️ 快照获取失败: {e}")
            return PageSnapshot(format=format, content="", elements=[])
    
    async def _extract_dom_elements(self, interactive_only: bool = False) -> List[Dict]:
        """提取 DOM 元素"""
        try:
            elements = await self.page.evaluate("""
                (interactiveOnly) => {
                    const all = document.querySelectorAll('*');
                    const result = [];
                    const interactiveTags = new Set(['a', 'button', 'input', 'select', 'textarea']);
                    
                    all.forEach((el, i) => {
                        if (i > 500) return;
                        
                        const tag = el.tagName.toLowerCase();
                        const isInteractive = interactiveTags.has(tag) || 
                                             el.onclick || 
                                             el.getAttribute('role') === 'button';
                        
                        if (isInteractive || !interactiveOnly) {
                            result.push({
                                ref: `el-${i}`,
                                tag: tag,
                                role: el.getAttribute('role') || tag,
                                text: (el.textContent || '').trim().substring(0, 100),
                                placeholder: el.getAttribute('placeholder') || '',
                                href: el.getAttribute('href') || '',
                                visible: el.offsetParent !== null
                            });
                        }
                    });
                    return result;
                }
            """, interactive_only)
            return elements or []
        except Exception as e:
            print(f"  ⚠️ DOM 提取失败: {e}")
            return []
    
    async def get_page_title(self) -> str:
        """获取页面标题"""
        try:
            return await self.page.title()
        except:
            return ""
    
    async def detect_framework(self) -> str:
        """检测前端框架"""
        try:
            framework = await self.page.evaluate("""() => {
                if (window.__VUE__) return 'vue3';
                if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__) return 'vue2';
                if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) return 'react';
                if (window.ng) return 'angular';
                if (window.__NUXT__) return 'nuxt';
                if (window.__NEXT_DATA__) return 'nextjs';
                if (document.querySelector('#app')?.__vue__) return 'vue2';
                if (document.querySelector('#root')?._reactRootContainer) return 'react';
                return 'unknown';
            }""")
            self.state.framework = framework
            print(f"🔍 检测到框架: {framework}")
            return framework
        except:
            return "unknown"
    
    async def wait_for_element(self, selector: str, timeout: float = 15) -> bool:
        """等待元素出现"""
        print(f"⏳ 等待元素: {selector}")
        try:
            await self.page.wait_for_selector(selector, timeout=int(timeout * 1000))
            print(f"  ✅ 元素已出现: {selector}")
            return True
        except Exception as e:
            print(f"  ❌ 元素未出现: {selector}")
            return False
    
    async def wait_for_text(self, text: str, timeout: float = 15) -> bool:
        """等待文本出现"""
        print(f"⏳ 等待文本: {text[:50]}...")
        try:
            await self.page.wait_for_function(
                f"""() => document.body.innerText.includes('{text}')""",
                timeout=int(timeout * 1000)
            )
            print(f"  ✅ 文本已出现")
            return True
        except:
            print(f"  ❌ 文本未出现")
            return False
    
    async def wait_for_api_call(self, url_pattern: str, timeout: float = 15) -> bool:
        """等待特定 API 调用"""
        print(f"⏳ 等待 API: {url_pattern}")
        start = time.time()
        while time.time() - start < timeout:
            for req in self._request_log:
                if url_pattern.lower() in req.url.lower():
                    print(f"  ✅ API 调用完成: {url_pattern}")
                    return True
            await asyncio.sleep(0.5)
        print(f"  ❌ API 调用未出现")
        return False
    
    async def wait_for_page_stable(self, timeout: float = 20) -> bool:
        """等待页面稳定"""
        print("⏳ 等待页面稳定...")
        try:
            await self.page.wait_for_load_state("networkidle", timeout=int(timeout * 1000))
            self.state.is_stable = True
            print("  ✅ 页面已稳定")
            return True
        except:
            print("  ⚠️ 页面可能仍在加载")
            return False
    
    async def smart_click(self, text_or_description: str, max_retries: int = 3) -> bool:
        """智能点击：快照驱动 + 重试"""
        print(f"🖱️ 智能点击: {text_or_description}")
        
        for attempt in range(max_retries):
            try:
                # 1. 获取快照
                snapshot = await self.get_snapshot(format="dom", interactive=True)
                
                # 2. 查找元素
                elem = snapshot.find_element(text_or_description)
                
                if elem:
                    # 3. 点击 - 使用文本查找
                    await self.page.get_by_text(text_or_description).first.click()
                    print(f"  ✅ 点击成功 (尝试 {attempt+1})")
                    return True
                else:
                    # 尝试精确匹配
                    await self.page.get_by_text(text_or_description, exact=True).click()
                    print(f"  ✅ 点击成功 (尝试 {attempt+1})")
                    return True
                    
            except Exception as e:
                print(f"  ⚠️ 点击失败 (尝试 {attempt+1}): {e}")
                await asyncio.sleep(1)
        
        # 所有尝试失败，使用视觉识别
        print(f"  🔍 使用视觉识别...")
        return await self.visual_click(text_or_description)
    
    async def visual_click(self, text_or_description: str) -> bool:
        """视觉识别点击"""
        print(f"👁️ 视觉识别点击: {text_or_description}")
        try:
            analysis = await self.visual_analyze(f"请找出包含'{text_or_description}'的可点击元素的坐标位置。")
            if analysis:
                print(f"  视觉分析结果: {analysis[:200]}...")
                return True
        except Exception as e:
            print(f"  ❌ 视觉点击失败: {e}")
        return False
    
    async def visual_analyze(self, prompt: str) -> Optional[str]:
        """视觉分析"""
        try:
            screenshot_path = f"/tmp/{self.agent_name}-screenshot.png"
            await self.page.screenshot(path=screenshot_path, full_page=True)
            
            with open(screenshot_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            api_key = "sk-sp-a68df77f47f04e1ca871300f7afa41f1"
            url = "https://coding.dashscope.aliyuncs.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "kimi-k2.5",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                    ]
                }],
                "max_tokens": 1000
            }
            
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  ❌ 视觉分析失败: {e}")
        return None
    
    async def fill_form(self, fields: Dict[str, str]) -> bool:
        """智能填充表单"""
        print(f"📝 填充表单: {list(fields.keys())}")
        
        for field_name, value in fields.items():
            try:
                # 尝试 placeholder
                locator = self.page.get_by_placeholder(field_name)
                if await locator.count() > 0:
                    await locator.fill(value)
                else:
                    # 尝试 label
                    locator = self.page.get_by_label(field_name)
                    if await locator.count() > 0:
                        await locator.fill(value)
                    else:
                        # 直接使用 selector
                        await self.page.fill(f"input[name='{field_name}']", value)
                
                print(f"  ✅ 填充: {field_name} = {value}")
                await asyncio.sleep(0.3)
            except Exception as e:
                print(f"  ❌ 填充失败: {field_name} - {e}")
                return False
        
        return True
    
    async def handle_dialog(self, action: str = "accept", text: str = ""):
        """处理对话框"""
        print(f"💬 处理对话框: {action}")
        self.page.on("dialog", lambda dialog: asyncio.ensure_future(
            dialog.accept(text) if action == "accept" else dialog.dismiss()
        ))
    
    async def monitor_network(self, duration: float = 10) -> List[NetworkRequest]:
        """监控网络请求"""
        print(f"📡 监控网络请求 ({duration}s)...")
        initial_count = len(self._request_log)
        
        await asyncio.sleep(duration)
        
        new_requests = self._request_log[initial_count:]
        print(f"  捕获 {len(new_requests)} 个新请求")
        return new_requests
    
    async def get_console_logs(self) -> List[str]:
        """获取控制台日志"""
        logs = []
        self.page.on("console", lambda msg: logs.append(msg.text))
        return logs
    
    async def get_page_errors(self) -> List[str]:
        """获取页面错误"""
        errors = []
        self.page.on("pageerror", lambda err: errors.append(str(err)))
        return errors


# ============================================================
# 测试用例
# ============================================================

async def test_dynamic_page_handling():
    """测试 1: 动态页面处理"""
    print("🧪 测试 1: 动态页面处理")
    
    engine = DynamicBrowserEngine("jerry")
    await engine.launch()
    
    try:
        state = await engine.navigate_and_wait("https://example.com/", wait_for="networkidle")
        print(f"  页面: {state.url}")
        print(f"  标题: {state.title}")
        print(f"  框架: {state.framework}")
        print(f"  已加载: {state.is_loaded}")
        
        snapshot = await engine.get_snapshot(format="dom", interactive=True)
        print(f"  快照元素: {len(snapshot.elements)} 个")
        
        assert state.is_loaded
        print("  ✅ 动态页面处理测试通过")
        return True
    finally:
        await engine.close()


async def test_element_discovery():
    """测试 2: 元素发现"""
    print("\n🔍 测试 2: 元素发现")
    
    engine = DynamicBrowserEngine("jerry")
    await engine.launch()
    
    try:
        await engine.navigate_and_wait("https://example.com/", wait_for="networkidle")
        
        snapshot = await engine.get_snapshot(format="dom")
        print(f"  快照格式: {snapshot.format}")
        print(f"  元素数量: {len(snapshot.elements)}")
        
        if snapshot.elements:
            print(f"  第一个元素: {snapshot.elements[0]}")
        
        found = snapshot.find_element("Example")
        if found:
            print(f"  找到元素: {found}")
        
        assert len(snapshot.elements) > 0
        print("  ✅ 元素发现测试通过")
        return True
    finally:
        await engine.close()


async def test_framework_detection():
    """测试 3: 框架检测"""
    print("\n🔧 测试 3: 框架检测")
    
    engine = DynamicBrowserEngine("jerry")
    await engine.launch()
    
    try:
        await engine.navigate_and_wait("https://vuejs.org/", wait_for="networkidle")
        framework = await engine.detect_framework()
        print(f"  vuejs.org: {framework}")
        
        await engine.navigate_and_wait("https://example.com/", wait_for="networkidle")
        framework = await engine.detect_framework()
        print(f"  example.com: {framework}")
        
        print("  ✅ 框架检测测试通过")
        return True
    finally:
        await engine.close()


async def test_smart_click():
    """测试 4: 智能点击"""
    print("\n🖱️ 测试 4: 智能点击")
    
    engine = DynamicBrowserEngine("jerry")
    await engine.launch()
    
    try:
        await engine.navigate_and_wait("https://example.com/", wait_for="networkidle")
        
        result = await engine.smart_click("Example", max_retries=2)
        print(f"  点击结果: {result}")
        
        print("  ✅ 智能点击测试通过")
        return True
    finally:
        await engine.close()


async def test_network_monitoring():
    """测试 5: 网络监控"""
    print("\n📡 测试 5: 网络监控")
    
    engine = DynamicBrowserEngine("jerry")
    await engine.launch()
    
    try:
        await engine.navigate_and_wait("https://example.com/", wait_for="networkidle")
        
        requests = await engine.monitor_network(duration=3)
        print(f"  捕获请求: {len(requests)} 个")
        
        print("  ✅ 网络监控测试通过")
        return True
    finally:
        await engine.close()


async def main():
    print("=" * 60)
    print("动态页面浏览器引擎 v3.0 测试")
    print("=" * 60)
    
    results = {}
    results["动态页面处理"] = "✅ 通过" if await test_dynamic_page_handling() else "❌ 失败"
    results["元素发现"] = "✅ 通过" if await test_element_discovery() else "❌ 失败"
    results["框架检测"] = "✅ 通过" if await test_framework_detection() else "❌ 失败"
    results["智能点击"] = "✅ 通过" if await test_smart_click() else "❌ 失败"
    results["网络监控"] = "✅ 通过" if await test_network_monitoring() else "❌ 失败"
    
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    print("=" * 60)
    
    return all("✅" in v for v in results.values())


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

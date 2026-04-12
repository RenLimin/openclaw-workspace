#!/usr/bin/env python3
"""
Ella 🦊 泛微 OA 浏览器自动化脚本 v1.0

功能：
1. 自动登录泛微 OA 系统
2. 提取合同信息 (合同附件、分项记录)
3. 导出合同数据为 CSV

导航路径：
1. 登录 → OA 主页面
2. 左侧导航：销售合同管理系统 → 合同基本信息管理 → 合同台账（销售）
3. 搜索合同编号 → 进入合同详情
4. 提取合同附件 → 下载
5. 返回 → 销售合同分项查询 → 提取分项记录
"""
import os
import sys
import json
import csv
import time
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

# ============================================================
# 配置
# ============================================================

OA_URL = "https://oa.bangcle.com/"
IAM_URL = "https://iam.bangcle.com/"
OUTPUT_DIR = "/Users/bangcle/.openclaw/workspace/training-reports/ella"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ELLAOAAutomation:
    """泛微 OA 浏览器自动化"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
    
    async def launch(self):
        """启动浏览器"""
        self.playwright = await async_playwright().start()
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=os.path.expanduser("~/.openclaw/browser-data/ella/"),
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.page = await self.context.new_page()
        print("🌐 Ella 专属浏览器已启动")
        return self
    
    async def login(self, username=None, password=None):
        """登录 OA 系统"""
        print("🔐 尝试登录泛微 OA...")
        
        # 检查 Keychain 凭证
        if not username:
            import subprocess
            try:
                result = subprocess.run(
                    ['security', 'find-generic-password', '-s', 'openclaw-browser-ella-oa-username', '-w'],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    username = result.stdout.strip()
            except:
                pass
        
        if not username:
            print("  ⚠️ 未找到 Keychain 凭证")
            print("  请 Rex 提供 OA 账号密码:")
            print("  security add-generic-password -s 'openclaw-browser-ella-oa-username' -a 'ella' -w '<账号>' -U")
            print("  security add-generic-password -s 'openclaw-browser-ella-oa-password' -a 'ella' -w '<密码>' -U")
            return False
        
        # 导航到登录页
        try:
            await self.page.goto(OA_URL, wait_until="domcontentloaded", timeout=30000)
        except:
            await self.page.goto(IAM_URL, wait_until="domcontentloaded", timeout=30000)
        
        # 等待登录表单
        try:
            await self.page.wait_for_selector('input[type="text"], input[type="email"], input[name*="user"], input[name*="account"]', timeout=10000)
            
            # 查找用户名和密码输入框
            username_input = await self.page.query_selector('input[type="text"], input[type="email"]')
            password_input = await self.page.query_selector('input[type="password"]')
            
            if username_input and password_input:
                await username_input.fill(username)
                await password_input.fill(password)
                await self.page.click('button[type="submit"], input[type="submit"]')
                await self.page.wait_for_load_state("networkidle")
                print("  ✅ 登录成功")
                return True
            else:
                print("  ❌ 未找到登录表单")
                return False
        except Exception as e:
            print(f"  ❌ 登录失败: {e}")
            return False
    
    async def navigate_to_contract_list(self):
        """导航到合同列表页"""
        print("📋 导航到合同台账...")
        
        # 等待主页面加载
        await self.page.wait_for_load_state("domcontentloaded")
        
        # 点击左侧导航：销售合同管理系统 → 合同基本信息管理 → 合同台账（销售）
        try:
            # 尝试查找菜单项
            await self.page.click('text=销售合同管理系统', timeout=10000)
            await self.page.click('text=合同基本信息管理', timeout=10000)
            await self.page.click('text=合同台账（销售）', timeout=10000)
            await self.page.wait_for_load_state("networkidle")
            print("  ✅ 已导航到合同列表页")
            return True
        except Exception as e:
            print(f"  ❌ 导航失败: {e}")
            # 截图以便调试
            await self.page.screenshot(path=f"{OUTPUT_DIR}/oa-navigation-error.png")
            return False
    
    async def search_contract(self, contract_number):
        """搜索合同"""
        print(f"🔍 搜索合同: {contract_number}")
        
        try:
            # 输入合同编号并回车
            search_box = await self.page.query_selector('input[placeholder*="合同编号"]')
            if search_box:
                await search_box.fill(contract_number)
                await self.page.keyboard.press('Enter')
                await self.page.wait_for_load_state("networkidle")
                
                # 点击合同编号进入详情
                contract_link = await self.page.query_selector(f'text={contract_number}')
                if contract_link:
                    # 新标签页
                    async with self.page.context.wait_for_event("page") as new_page_info:
                        await contract_link.click()
                    detail_page = new_page_info.value
                    await detail_page.wait_for_load_state("networkidle")
                    print("  ✅ 已进入合同详情页")
                    return detail_page
            return None
        except Exception as e:
            print(f"  ❌ 搜索失败: {e}")
            return None
    
    async def extract_contract_attachments(self, detail_page):
        """提取合同附件"""
        print("📎 提取合同附件...")
        
        try:
            # 导航到：基本信息 → 合同文件归档 → 合同扫描件文件
            await detail_page.click('text=合同文件归档', timeout=10000)
            await detail_page.click('text=合同扫描件文件', timeout=10000)
            
            # 监听下载事件
            downloads = []
            async with detail_page.context.expect_download() as download_info:
                # 悬浮并点击下载按钮
                download_button = await detail_page.query_selector('text=下载')
                if download_button:
                    await download_button.hover()
                    await download_button.click()
            
            download = await download_info.value
            download_path = f"{OUTPUT_DIR}/contract-{download.suggested_filename}"
            await download.save_as(download_path)
            print(f"  ✅ 附件已下载: {download.suggested_filename}")
            return download_path
        except Exception as e:
            print(f"  ❌ 附件提取失败: {e}")
            return None
    
    async def extract_contract_items(self, contract_number):
        """提取合同分项记录"""
        print("📊 提取合同分项记录...")
        
        try:
            # 导航到：销售合同管理系统 → 合同基本信息管理 → 销售合同分项查询
            await self.page.goto(OA_URL, wait_until="domcontentloaded")
            await self.page.click('text=销售合同管理系统', timeout=10000)
            await self.page.click('text=合同基本信息管理', timeout=10000)
            await self.page.click('text=销售合同分项查询', timeout=10000)
            await self.page.wait_for_load_state("networkidle")
            
            # 搜索合同编号
            search_box = await self.page.query_selector('input[placeholder*="合同编号"]')
            if search_box:
                await search_box.fill(contract_number)
                await self.page.keyboard.press('Enter')
                await self.page.wait_for_load_state("networkidle")
            
            # 提取表格数据
            table_data = await self.page.evaluate('''() => {
                const rows = document.querySelectorAll('table tr, .el-table__row');
                const data = [];
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td, th');
                    const rowData = [];
                    cells.forEach(cell => rowData.push(cell.textContent.trim()));
                    if (rowData.length > 0) data.push(rowData);
                });
                return data;
            }''')
            
            print(f"  ✅ 提取到 {len(table_data)} 行数据")
            return table_data
        except Exception as e:
            print(f"  ❌ 分项提取失败: {e}")
            return []
    
    async def export_to_csv(self, data, filename="合同分项导出数据.csv"):
        """导出为 CSV"""
        output_path = f"{OUTPUT_DIR}/{filename}"
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow(row)
        print(f"  ✅ CSV 已导出: {output_path}")
        return output_path
    
    async def close(self):
        """关闭浏览器"""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        print("🔒 浏览器已关闭")


async def main():
    """主函数"""
    print("=" * 60)
    print("Ella 🦊 泛微 OA 浏览器自动化")
    print("=" * 60)
    
    automation = ELLAOAAutomation()
    await automation.launch()
    
    # 测试登录
    login_success = await automation.login()
    if login_success:
        # 测试合同查询
        # contract_page = await automation.search_contract("XSZS2511120891-3")
        # if contract_page:
        #     await automation.extract_contract_attachments(contract_page)
        #     items_data = await automation.extract_contract_items("XSZS2511120891-3")
        #     await automation.export_to_csv(items_data)
        pass
    
    await automation.close()


if __name__ == "__main__":
    asyncio.run(main())

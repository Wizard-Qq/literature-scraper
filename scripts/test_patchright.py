#!/usr/bin/env python3
"""使用 patchright 直接访问 Science.org"""
from patchright.sync_api import sync_playwright
import time

print("使用 Patchright 访问 Science.org...")

with sync_playwright() as p:
    # 启动浏览器
    browser = p.chromium.launch(
        headless=True,
        args=[
            '--disable-blink-features=AutomationDetectionControl',
            '--no-sandbox',
            '--disable-dev-shm-usage'
        ]
    )
    
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    )
    
    page = context.new_page()
    
    # 访问 Science.org
    print("访问 https://www.science.org/news ...")
    start = time.time()
    
    try:
        response = page.goto("https://www.science.org/news", wait_until="networkidle", timeout=180000)
        elapsed = time.time() - start
        
        print(f"状态码：{response.status}")
        print(f"耗时：{elapsed:.1f} 秒")
        
        # 获取页面内容
        content = page.content()
        print(f"页面大小：{len(content)} 字节")
        
        if "Just a moment" in content:
            print("\n❌ 被 Cloudflare 拦截")
        elif "<title" in content:
            print("\n✅ 访问成功!")
            title = page.title()
            print(f"页面标题：{title[:100]}")
            
            # 尝试查找文章链接
            links = page.query_selector_all("a[href*='/news/']")
            print(f"找到新闻链接：{len(links)} 个")
            for link in links[:5]:
                href = link.get_attribute('href')
                text = link.inner_text().strip()[:50]
                print(f"  - {text}... ({href[:60]})")
        
        # 保存页面
        page.screenshot(path="/tmp/science_test.png")
        print("\n截图已保存：/tmp/science_test.png")
        
    except Exception as e:
        print(f"错误：{e}")
        import traceback
        traceback.print_exc()
    
    browser.close()

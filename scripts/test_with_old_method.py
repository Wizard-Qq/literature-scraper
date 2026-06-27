#!/usr/bin/env python3
"""使用旧脚本的成功方法测试 Science.org"""
from scrapling.fetchers import StealthyFetcher
import time

# 找一个实际的 Science 文章 URL（Latest News）
TEST_URL = "https://www.science.org/news"

print("="*70)
print(f"Testing: {TEST_URL}")
print("="*70)

fetcher = StealthyFetcher()

start = time.time()
print("开始获取页面...")

try:
    response = fetcher.fetch(
        TEST_URL,
        solve_cloudflare=True,
        timeout=300000,
        wait=120000,  # 2 分钟等待
        load_dom=True,
        headless=True,
        network_idle=True
    )
    
    elapsed = time.time() - start
    print(f"耗时：{elapsed:.1f} 秒")
    print(f"状态码：{response.status}")
    
    if response.body:
        print(f"响应大小：{len(response.body)} 字节")
        
        content = response.body.decode('utf-8', errors='ignore')
        
        if "Just a moment" in content or "Verifying" in content:
            print("\n❌ 仍被 Cloudflare 拦截")
            # 显示前 500 字符
            print(content[:500])
        else:
            print("\n✅ 成功获取页面!")
            
            # 尝试提取链接
            import re
            links = re.findall(r'href="(/news/[^"]+)"', content)
            print(f"找到新闻链接：{len(links)} 个")
            
            for link in links[:5]:
                print(f"  - https://www.science.org{link}")
        
    else:
        print("❌ 响应体为空")
        
except Exception as e:
    print(f"❌ 错误：{e}")
    import traceback
    traceback.print_exc()

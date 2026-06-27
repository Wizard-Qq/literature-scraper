#!/usr/bin/env python3
"""测试 Science.org - 更长等待时间"""
from scrapling import StealthyFetcher
import time

print("测试 Science.org 访问（长等待）...")

fetcher = StealthyFetcher(
    headless=True,
    disable_resources=False,  # 启用资源加载
    timeout=300000,
    wait=180000,  # 3 分钟等待
    solve_cloudflare=True,
    network_idle=True,  # 等待网络空闲
)

print("访问 https://www.science.org/news ...")
start = time.time()

try:
    response = fetcher.fetch("https://www.science.org/news")
    elapsed = time.time() - start
    
    print(f"状态码：{response.status}")
    print(f"耗时：{elapsed:.1f} 秒")
    print(f"响应大小：{len(response.body) if response.body else 0} 字节")
    
    if response.status == 200 and response.body:
        content = response.body.decode('utf-8', errors='ignore')
        
        # 检查是否成功
        if "Just a moment" in content:
            print("\n❌ 仍被 Cloudflare 拦截")
        elif "<title" in content:
            print("\n✅ 可能成功！")
            # 尝试提取标题
            import re
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', content)
            if title_match:
                print(f"页面标题：{title_match.group(1)[:100]}")
        
        print(f"\n前 500 字符:")
        print("-" * 60)
        print(content[:500])
        
    else:
        print(f"响应异常：status={response.status}")
        
except Exception as e:
    print(f"错误：{e}")
    import traceback
    traceback.print_exc()

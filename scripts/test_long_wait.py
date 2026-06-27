#!/usr/bin/env python3
"""使用经过验证的成功参数测试 Science.org"""
from scrapling.fetchers import StealthyFetcher
import time

TEST_URL = "https://www.science.org/doi/10.1126/science.ads0532"

print("="*70)
print(f"Testing: {TEST_URL}")
print(f"参数：timeout=300s, wait=180s, solve_cloudflare=True")
print("="*70)

start = time.time()
fetcher = StealthyFetcher()

try:
    print("开始获取页面 (最多等待 5 分钟)...")
    response = fetcher.fetch(
        TEST_URL,
        solve_cloudflare=True,
        timeout=300000,  # 5 分钟
        wait=180000,     # 3 分钟等待
        load_dom=True,
        headless=True,
        network_idle=True
    )
    
    elapsed = time.time() - start
    print(f"\n耗时：{elapsed:.1f} 秒")
    print(f"状态码：{response.status}")
    
    if response.body:
        body_size = len(response.body)
        print(f"响应大小：{body_size} 字节")
        
        content = response.body.decode('utf-8', errors='ignore')
        
        # 检查是否成功
        if "Just a moment" in content or "Verifying" in content or "Cloudflare" in content:
            print("\n❌ 仍被 Cloudflare 拦截")
            print(content[:500])
        else:
            print("\n✅ 成功获取页面!")
            
            # 尝试提取标题
            import re
            title = re.search(r'<title[^>]*>([^<]+)</title>', content)
            if title:
                print(f"标题：{title.group(1)[:100]}")
            
            # 保存 HTML
            with open('/tmp/science_success_test.html', 'wb') as f:
                f.write(response.body)
            print("已保存到 /tmp/science_success_test.html")
    else:
        print("❌ 响应体为空")
        
except Exception as e:
    print(f"❌ 错误：{e}")
    import traceback
    traceback.print_exc()

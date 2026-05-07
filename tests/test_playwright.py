import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


async def test_playwright_connectivity():
    """Playwright 内核连通性测试"""
    async with async_playwright() as p:
        # 启动浏览器内核 (headless=True 可以后台运行，不弹窗)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # 访问一个极简的目标网站
            await page.goto("https://example.com", wait_until="domcontentloaded") # `domcontentloaded`: 等待HTML解析完成, 这比默认的 `load` (等待所有资源) 更快

            # 执行最简单的JS：获取页面标题
            title = await page.title()
            print(f"\n✅ Playwright 环境就绪！页面标题是: '{title}'")
        except PlaywrightTimeoutError:
            print("❌ 测试失败：操作超时。请检查网络连接和目标地址是否可达。")
        except Exception as e:
            print(f"❌ 测试失败，捕获到未知异常：{type(e).__name__}: {e}")
        finally:
            # 确保即使出现异常, 浏览器也能被关闭
            if browser:
                await browser.close()
                print("浏览器资源已释放。")


if __name__ == "__main__":
    asyncio.run(test_playwright_connectivity())
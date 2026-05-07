from movie.client import Requests
import asyncio

async def test_client_connectivity():
    """测试客户端能否正常发起请求"""
    async with Requests() as client:
        resp = await client.client.get("https://httpbin.org/get")
        assert resp.status_code == 200, f"状态码: {resp.status_code} | 响应预览: {resp.text[:500]}"
        print("✅ 客户端连通性测试通过")

if __name__ == "__main__":
    asyncio.run(test_client_connectivity())
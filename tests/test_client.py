from movie.client import Requests
import pytest


@pytest.mark.asyncio
async def test_client_connectivity():
    """测试客户端能否正常发起请求"""
    async with Requests() as client:
        resp = await client._client.get("https://example.com", timeout=5)
        assert resp.status_code == 200, f"状态码: {resp.status_code} | 响应预览: {resp.text[:500]}"

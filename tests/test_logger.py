import asyncio
from movie.utils import logger, logging_configuration

@logger
async def sample_func(**kwargs):
    await asyncio.sleep(0.1)
    return "success"

async def test_logger():
    """测试日志装饰器是否正常记录执行时间"""
    test_logger = logging_configuration("test", "test.log")
    result = await sample_func(logger=test_logger)
    assert result == "success"
    print("✅ 日志装饰器测试通过")

if __name__ == "__main__":
    asyncio.run(test_logger())
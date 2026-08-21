from movie.utils import logger, logging_configuration

import pytest

import asyncio


@logger
async def sample_func(**kwargs):
    await asyncio.sleep(0.1)
    return "success"

@pytest.mark.asyncio
async def test_logger(tmp_path):
    """测试日志装饰器是否正常记录执行时间"""
    # 在临时目录里生成日志文件
    log_file = tmp_path / "test_log.log"

    test_logger = logging_configuration("test_log", str(log_file))
    result = await sample_func(logger=test_logger)

    assert result == "success"

    # 验证文件确实被写入了
    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "sample_func" in content  # 验证装饰器记录了函数名
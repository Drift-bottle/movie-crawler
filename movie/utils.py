import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from playwright.async_api import async_playwright
import time
import logging
from functools import wraps
from typing import Callable, Any, List

"""
movie-crawler 通用工具模块:
提供日志配置、计时装饰器、Cookie 获取 (Edge 浏览器) 等可复用功能。
"""

# ------手动配置日志------
def logging_configuration(logger_name=None, log_file_name=None):
    """
    Args:
        logger_name: 创建的 Logger 名称
        log_file_name: 日志文件的名称
    """
    # 创建 Logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 屏蔽debug信息
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('tenacity').setLevel(logging.WARNING)
    logging.getLogger('chardet').setLevel(logging.WARNING)
    logging.getLogger('pandas').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

    # 创建文件处理器
    file_handler = logging.FileHandler(
        log_file_name,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 配置日志格式
    formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 添加到 Logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def logger(func: Callable[..., Any]) -> Callable[..., Any]:
    """日志计时装饰器, 记录函数执行时间"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 获取 logger
        courier_logger = kwargs.pop('logger', logging.getLogger(__name__))
        # 函数开始执行时间
        start_time = time.perf_counter()
        try:
            # 调用函数
            result = await func(*args, **kwargs)
            # 函数执行结束时间
            end_time = time.perf_counter()
            sum_time = end_time - start_time
            courier_logger.debug(f"函数 {func.__name__} 执行时间: {sum_time:.6f}秒")
            return result
        except Exception as e:
            end_time = time.perf_counter()
            sum_time = end_time - start_time
            courier_logger.error(f"❌函数 {func.__name__} 执行时出现异常 | {type(e).__name__}: {e} | 执行时间: {sum_time:.6f}秒")
            raise e
    return wrapper


# ------获取cookies------
# 储存当前 cookies
_current_cookies = httpx.Cookies()

@retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type(Exception),
        reraise=True  # 达到最大重试次数后抛出原始异常
    )
@logger
async def get_position_with_edge_login(target_domains: List[str], **kwargs):
    """
        复用edge登录态获取cookies
        Args:
            target_domains: 储存目标网站域的列表
            kwargs: logger(供 @logger 使用)
    """
    # 获取 logger
    courier_logger = kwargs.pop('cookies_logger', logging.getLogger(__name__))
    async with async_playwright() as p:
        # 清除上一次获取的 cookies
        _current_cookies.clear()

        # 连接已打开的 edge 浏览器
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")

        # 获取浏览器上下文中的 cookies
        context = browser.contexts[0]
        cookies = await context.cookies()

        # 转化为 httpx 可用形式 | 只保留关键认证 cookie, 大幅减小体积
        cookies_list = [c for c in cookies if any(c.get('domain', '').endswith(d) for d in target_domains)]
        if cookies_list:
            for c in cookies_list:
                _current_cookies.set(
                    c['name'],
                    c['value'],
                    domain=c.get('domain', None),
                    path=c.get('path', None),
                )
            return _current_cookies
        else:
            err = "❌_current_cookies未存取cookies, 可能未登录或已过期"
            courier_logger.error(err)
            raise Exception(err)

import httpx
from httpx import Cookies
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import chardet
from .utils import logger
import logging


# ------设置请求类------
class Requests:
    """
    movie-crawler 公共请求客户端。

    依赖 httpx 实现异步 HTTP 请求, 集成了:
      - 智能编码检测 (chardet + 手动 fallback)
      - 可选的 Cookie 注入
      - 请求/响应网络耗时监控 (event_hooks)
      - robots.txt 校验
      - 基于 tenacity 的指数退避重试
    """
    def __init__(self, cookies: Cookies=None, logger=None):
        # 设置请求前钩子, 统一会话
        self.client = httpx.AsyncClient(
            default_encoding=self.smart_encoding_detect,
            cookies=cookies,
            event_hooks={
                'request': [self._hook_start_time],
                'response': [self._hook_end_time]
            },
            timeout=10
        )
        # 设置 logger
        self.logger = logger or logging.getLogger(__name__)

    # 请求钩子
    async def _hook_start_time(self, request: httpx.Request) -> None:
        request.headers['x-by-start'] = str(time.perf_counter())

    # 响应钩子
    async def _hook_end_time(self, response: httpx.Response) -> None:
        start = float(response.request.headers.get('x-by-start', 0))
        sum_time = time.perf_counter() - start
        self.logger.debug(f"{response.request.url}耗时: {sum_time:.6f}秒")

    # 上下文管理器
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    # 判断网页是否允许被抓取(url/robots.txt)
    async def can_fetch(self, url: str, **kwargs):
        """
        判断给定的 user-agent 是否允许抓取url
        Args:
            url: 用于检验是否允许爬取的 url
            kwargs: headers请求头, logger(供 @logger 使用)
        """
        headers = kwargs.get('headers', {})
        user_agent = headers.get('User-Agent', 'Mozilla/5.0 ...')

        # 提取域名,构建 robots.txt 的完整url
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = f"{base}/robots.txt"

        rp = RobotFileParser()
        rp.set_url(robots_url)

        try:
            rp.read()
        except Exception as e:
            self.logger.error(f"❌读取 robots.txt 失败 | {type(e).__name__}: {e}")
            raise e

        return rp.can_fetch(user_agent, url) # 返回True,则允许爬取

    def smart_encoding_detect(self, content: bytes):
        """
            智能编码检测器, 集成 Fallback 逻辑
            Args:
                content: 目标网站返回的 bytes数据
        """
        self.logger.debug(f"调试: smart_encoding_detect 被调用! 内容长度: {len(content)}")

        # 先用 chardet 检测, 获取置信度
        result = chardet.detect(content[:4000])
        encoding = result.get('encoding')
        confidence = result.get('confidence')

        # Fallback 逻辑, 如果置信度高, 直接返回
        if encoding and confidence > 0.9:
            return encoding

        # 如果置信度不高或无结果, 手动解码
        encodings_to_try = ["utf-16", "gb2312", "gbk", "utf-8"]
        for enc in encodings_to_try:
            try:
                content.decode(enc)
                return enc
            except Exception as e:
                self.logger.error(f"❌手动解码失败: 尝试的编码: {enc} | {type(e).__name__}: {e}")

        return None # 如果全部失败, 让 httpx 用 utf-8


    # 为解析类提供接口
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type(Exception),
        reraise=True # 达到最大重试次数后抛出原始异常
    )
    @logger
    async def inter_face(self, url: str, key_message: str, **kwargs):
        """
        Args:
            url: 用于发送请求的 url
            key_message: 目标网站页面的一个关键信息
            kwargs: headers请求头, logger(供 @logger 使用)
        """
        # 发送请求
        resp = await self.client.get(url, **kwargs)

        response_text = None
        # 尝试直接获取文本
        try:
            response_text = resp.text
        except Exception:
            raw_content = resp.content
            encodings_to_try = ["utf-16", "gb2312", "gbk", "utf-8"]
            for enc in encodings_to_try:
                try:
                    response_text = raw_content.decode(enc)
                    break
                except Exception as e:
                    self.logger.error(f"❌手动解码失败: 尝试的编码: {enc} | {type(e).__name__}: {e}")
                    continue
            else:
                # 当所有解码都失败时, 用 chardet 再次解码
                detected = chardet.detect(raw_content[:4000])
                if detected.get('encoding'):
                    response_text = raw_content.decode(detected['encoding'], errors='replace')
                else:
                    # 最终极 Fallback, 用 utf-8 解码, 忽视非法字符
                    response_text = raw_content.decode('utf-8', errors='replace')

        try:
            if resp.status_code == 200:
                if key_message not in response_text:
                    err = f"❌ 状态码为200,但可能遭遇反爬"
                    self.logger.error(err)
                    raise Exception(err)
                else:
                    return response_text
            else:
                err = f"❌请求失败,状态码；{resp.status_code} | 响应预览: {response_text[:500]}"
                # 打印前500个字符,查看是否包含异常提示
                self.logger.error(err)
        except Exception as e:
            self.logger.error(f"❌出现异常 | {type(e).__name__}: {e}")
            raise e
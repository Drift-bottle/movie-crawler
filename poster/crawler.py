from movie.client import Requests
from movie.utils import logger
from httpx import Cookies
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from bs4 import BeautifulSoup
import asyncio
import logging
import random
from models import PosterUrl


# ------继承请求类------
class Poster(Requests):
    def __init__(self, cookies: Cookies=None, logger=None):
        super().__init__(cookies=cookies, logger=logger) # 调用父类 Requests 的 __init__ 方法，传入 cookies 和 logger 依赖
        self._image_semaphore = asyncio.Semaphore(4) # 限制同时请求海报 url 的并发数为 4

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type(Exception),
        reraise=True  # 达到最大重试次数后抛出原始异常
    )
    @logger
    async def request_poster_url(self, url: str, **kwargs):
        """
        请求海报 url
        Args:
            url: 海报 url
            kwargs: headers请求头, logger(供 @logger 使用)
        """
        # 设置请求头
        headers = kwargs.get("headers", {})
        headers['referer'] = url
        async with self._image_semaphore: # 使用信号量控制并发
            poster_resp = await self.client.get(url, headers=headers, timeout=15)

            hex_str = poster_resp.content[:100].hex()
            # 把每两个十六进制字符后面加一个空格，方便阅读
            formatted_hex = ' '.join(hex_str[i:i + 2] for i in range(0, len(hex_str), 2))
            try:
                if poster_resp.status_code == 200:
                    content_type = poster_resp.headers.get('content-type', '')
                    return poster_resp.content, content_type
                else:
                    err = f"❌请求失败, 状态码: {poster_resp.status_code} | 响应内容前100字节(16进制): {formatted_hex}"
                    self.logger.error(err)
                    raise Exception(err)
            except Exception as e:
                self.logger.error(f"❌捕获到的异常: {type(e).__name__}: {e} | 响应内容前100字节(16进制): {formatted_hex}")
                raise e


# ------设置解析类------
class MoviePosterCrawler:
    """
    functions: 解析网页文本
    """
    def __init__(self, logger=None):
        self.all_data = set() # 用于标题和海报url数据去重
        self.data = [] # 储存最终电影数据
        self.logger = logger or logging.getLogger(__name__) # 设置 logger

    # 获取 title 和 post_url
    @logger
    async def fetch_page(self, resp, key_message, **kwargs):
        """
        抓取+解析网页数据
        Args:
            resp: 用于请求的 client
            key_message: 目标网站关键词
            kwargs: headers请求头, logger(供 @logger 使用)
        """
        page_num = 1
        url_list = ['...'] # 储存要请求的 url
        while True:
            self.logger.info(f"正在爬取第{page_num}页")

            # 暂时储存单个电影数据
            movies_list: list[PosterUrl] = []

            url = url_list[-1]
            # 判断网页是否允许被抓取(url/robots.txt)
            can_fetch = await resp.can_fetch(url, **kwargs)
            if can_fetch:
                self.logger.info(f"网页允许被抓取: {can_fetch}")
                # 获取网页html文件
                html_doc = await resp.inter_face(url, key_message, **kwargs, logger=self.logger)
                if html_doc is not None:
                    try:
                        # 开始解析网页
                        soup = BeautifulSoup(html_doc, 'lxml')
                        items = soup.select('CSS Selector')
                        for item in items:
                            # 获取标题
                            title_tag = item.select_one('CSS Selector')
                            if not title_tag:
                                self.logger.warning(f"未在第{page_num}页提取到 title 数据")
                                continue
                            title = title_tag.get_text(strip=True)

                            # 获取电影海报 url
                            poster_tag = item.select_one('CSS Selector')
                            if not poster_tag:
                                self.logger.warning(f"未在第{page_num}页提取到 poster_tag 数据")
                                continue
                            poster_url = poster_tag['Attribute']
                            if not poster_url:
                                self.logger.warning(f"未在第{page_num}页提取到 poster_url 数据")
                                continue

                            examine_data = (title, str(poster_url))
                            if examine_data not in self.all_data:
                                self.all_data.add(examine_data)

                                # 创建PosterUrl实例
                                movie = PosterUrl(title=title, poster_url=str(poster_url))
                                movies_list.append(movie)

                        self.data.extend(movies_list)
                        self.logger.info(f"请求 {url} 成功, ✅累积爬取 {len(self.data)} 条数据")

                        # 获取'下一页'url
                        next_tag = soup.select_one('CSS Selector')
                        if not next_tag:
                            self.logger.warning(f"未在第{page_num}页提取到 next_tag 数据")
                            break
                        params = next_tag.get('Attribute')
                        if params:
                            new_url = url_list[0] + str(params)
                            self.logger.info(f"当前页数: {page_num} | 成功获取下一页url | params: {params}")
                            url_list.append(new_url)
                        else:
                            self.logger.info("已爬取最后一页，停止翻页")
                            break
                    except Exception as e:
                        self.logger.error(f"❌解析异常 | {type(e).__name__}: {e}")
                        break
                else:
                    break
            else:
                self.logger.warning(f"网页不允许被爬取: {can_fetch}")
                break

            page_num += 1
            delay_time = random.uniform(1, 1.5)
            await asyncio.sleep(delay_time)

        return self.data
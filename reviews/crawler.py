from movie.client import Requests
from movie.utils import logger
from models import MovieReview, ReviewsCrawlerConfig

from httpx import Cookies
from bs4 import BeautifulSoup

import asyncio
import logging
import random
from typing import Optional
import os


# ------设置解析类------
class MovieReviewCrawler:
    """解析网页文本"""
    def __init__(
            self,
            cookies: Cookies,
            config: ReviewsCrawlerConfig,
            logger: Optional[logging.Logger] = None
    ) -> None:
        """
        初始化数据解析器

        Args:
            cookies: 所需的 cookies
            config: MovieRatingCrawlerConfig实例
            logger: logging.Logger实例
        """
        self._cookies = cookies  # 设置 cookies
        self._config = config
        self._logger = logger or logging.getLogger(__name__) # 设置 logger
        self._data_test = set()  # 用于数据去重
        self._data = []  # 储存最终电影数据

    @logger
    async def fetch_page(
            self,
            key_message: str,
            headers: dict,
            logger: Optional[logging.Logger] = None
    ) -> list | None:
        """
        抓取+解析网页数据

        Args:
            key_message: 目标网站关键词
            headers: headers请求头,
            logger: logger(供 @logger 使用)
        """
        page_num = 1
        url_list = [self._config.start_url]  # 储存要请求的 url
        async with Requests(cookies=self._cookies, logger=self._logger) as resp:
            while True:
                self._logger.info(f"正在爬取第{page_num}页")

                # 暂时储存单个电影数据
                movie_list: list[MovieReview] = []

                url = url_list[-1]
                basic_url = url_list[0].split('?')[0] # 用于拼接成新 url 的基本片段
                # 判断网页是否允许被抓取(url/robots.txt)
                can_fetch = await resp.can_fetch(url, headers)
                if can_fetch:
                    self._logger.info(f"网页允许被抓取: {can_fetch}")
                    # 获取网页html文件
                    html_doc = await resp.inter_face(url, key_message, headers, logger=self._logger)
                    if html_doc is not None:
                        try:
                            # 开始解析网页
                            soup = BeautifulSoup(html_doc, 'lxml')
                            items = soup.select(self._config.review_item_selector)
                            for item in items:
                                # 未评分或无内容的短评也算
                                # 获取评分(力荐，... ,未评分)
                                point_tag = item.select_one(self._config.rating_selector)
                                if not point_tag:
                                    self._logger.warning(f"第{page_num}页存在未评分的短评")
                                    continue
                                rating = point_tag.get(self._config.rating_attribute)

                                # 获取短评内容(......, 无内容)
                                content_tag = item.select_one(self._config.content_selector)
                                if not content_tag:
                                    self._logger.warning(f"第{page_num}页存在有评分, 但无评论内容的短评")
                                    continue
                                preview = content_tag.get_text(strip=True)

                                # 数据去重
                                examine_data = str((rating, preview))
                                if preview not in self._data_test:
                                    self._data_test.add(examine_data)

                                    # 创建 MovieReview 实例
                                    movie = MovieReview(rating=str(rating), review=str(preview))
                                    movie_list.append(movie)

                            self._data.extend(movie_list)
                            self._logger.info(f"请求 {url} 成功, ✅累积爬取 {len(self._data)} 条数据")

                            # 获取'下一页'url
                            next_tag = soup.select_one(self._config.next_url_selector)
                            if not next_tag:
                                self._logger.warning(f"未在第{page_num}页提取到 next_tag 数据")
                                break
                            params = next_tag.get(self._config.next_url_attribute)
                            if params:
                                new_url = os.path.join(basic_url, str(params))
                                self._logger.info(f"当前页数: {page_num} | 成功获取下一页url | params: {params}")
                                url_list.append(new_url)
                            else:
                                self._logger.info("已爬取最后一页，停止翻页")
                                break
                        except Exception as e:
                            self._logger.error(f"❌解析异常 | {type(e).__name__}: {e}")
                            break
                    else:
                        break
                else:
                    self._logger.warning(f"网页不允许被爬取: {can_fetch}")
                    break

                page_num += 1
                delay_time = random.uniform(1, 1.5)
                await asyncio.sleep(delay_time)

        return self._data
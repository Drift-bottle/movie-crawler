from movie import Requests, logger
from models import MovieRating, MovieRatingCrawlerConfig

from bs4 import BeautifulSoup

import asyncio
import logging
import random
from typing import Optional
import os


# ------设置解析类------
class MovieRatingCrawler:
    """解析网页文本"""
    def __init__(
            self,
            config: MovieRatingCrawlerConfig,
            logger: Optional[logging.Logger] = None
    ) -> None:
        """
        初始化数据解析器

        Args:
            config: MovieRatingCrawlerConfig实例
            logger: logging.Logger实例
        """
        self._config = config
        self._logger = logger or logging.getLogger(__name__) # 设置 logger
        self._title_data = set()  # 用于标题数据去重
        self._data = []  # 储存最终电影数据

    # 获取 title 和 rating
    @logger
    async def fetch_page(
            self,
            key_message: str,
            headers: dict,
            **kwargs
    ) -> list | None:
        """
        抓取+解析网页数据

        Args:
            key_message: 目标网站页面的一个关键信息
            headers: headers请求头
            **kwargs: logger(供 @logger 使用)
        """
        page_num = 1
        url_list = [self._config.start_url] # 储存要请求的 url
        async with Requests(logger=self._logger) as resp:
            while True:
                self._logger.info(f"正在爬取第{page_num}页")

                # 暂时储存单个电影数据
                movies_list: list[MovieRating] = []

                url = url_list[-1]
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
                            items = soup.select(self._config.movie_item_selector)
                            for item in items:
                                # 获取标题
                                title_tag = item.select_one(self._config.title_selector)
                                if not title_tag:
                                    self._logger.warning(f"未在第{page_num}页提取到 title 数据")
                                    continue
                                title = title_tag.get_text(strip=True)
                                if title not in self._title_data:
                                    self._title_data.add(title)

                                # 获取评分
                                rating_tag = item.select_one(self._config.rating_selector)
                                if not rating_tag:
                                    self._logger.warning(f"未在第{page_num}页提取到 point 数据")
                                    continue
                                rating = rating_tag.get_text(strip=True)

                                # 创建 MoveRating 实例
                                movie = MovieRating(title=title,rating=rating)
                                movies_list.append(movie)

                            self._data.extend(movies_list)
                            self._logger.info(f"请求 {url} 成功, ✅累积爬取 {len(self._data)} 条数据")

                            # 获取'下一页'url
                            next_tag = soup.select_one(self._config.next_url_selector)
                            if not next_tag:
                                self._logger.warning(f"未在第{page_num}页提取到 next_tag 数据")
                                break
                            params = next_tag.get(self._config.next_url_attribute)
                            if params:
                                new_url = os.path.join(url_list[0], str(params))
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
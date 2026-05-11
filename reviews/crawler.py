from movie.client import Requests
from movie.utils import logger
from httpx import Cookies
from bs4 import BeautifulSoup
import asyncio
import logging
import random
from models import MovieReview


# ------设置解析类------
class MovieReviewCrawler:
    """
    functions: 解析网页文本
    """
    def __init__(self, cookies: Cookies=None, logger=None):
        self.data_test = set() # 用于数据去重
        self.data = [] # 储存最终电影数据
        self.logger = logger or logging.getLogger(__name__) # 设置 logger
        self.cookies = cookies # 设置 cookies

    @logger
    async def fetch_page(self, key_message, **kwargs):
        """
        抓取+解析网页数据
        :param key_message: 目标网站关键词
        :param kwargs: headers请求头, logger(供 @logger 使用)
        """
        page_num = 1
        url_list = ['...']  # 储存要请求的 url
        async with Requests(cookies=self.cookies, logger=self.logger) as resp:
            while True:
                self.logger.info(f"正在爬取第{page_num}页")

                # 暂时储存单个电影数据
                movie_list: list[MovieReview] = []

                url = url_list[-1]
                basic_url = url_list[0].split('?')[0] # 用于拼接成新 url 的基本片段
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
                                # 未评分或无内容的短评也算
                                # 获取评分(力荐，... ,未评分)
                                point_tag = item.select_one('CSS Selector')
                                if not point_tag:
                                    self.logger.warning(f"第{page_num}页存在未评分的短评")
                                    continue
                                rating = point_tag.get('Attribute')

                                # 获取短评内容(......, 无内容)
                                preview_tag = item.select_one('CSS Selector')
                                if not preview_tag:
                                    self.logger.warning(f"第{page_num}页存在有评分, 但无评论内容的短评")
                                    continue
                                preview = preview_tag.get_text(strip=True)

                                # 数据去重
                                examine_data = str((rating, preview))
                                if preview not in self.data_test:
                                    self.data_test.add(examine_data)

                                    # 创建 MovieReview 实例
                                    movie = MovieReview(rating=str(rating), review=str(preview))
                                    movie_list.append(movie)

                            self.data.extend(movie_list)
                            self.logger.info(f"请求 {url} 成功, ✅累积爬取 {len(self.data)} 条数据")

                            # 获取'下一页'url
                            next_tag = soup.select_one('CSS Selector')
                            if not next_tag:
                                self.logger.warning(f"未在第{page_num}页提取到 next_tag 数据")
                                break
                            params = next_tag.get('Attribute')
                            if params:
                                new_url = basic_url + str(params)
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
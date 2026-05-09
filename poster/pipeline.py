from movie.utils import logger
from crawler import Poster, MoviePosterCrawler
import asyncio
import logging
import os
import random

# ------设置保存类------
class SaveData:
    """保存解析后的海报数据"""
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def _guess_extension(self, url: str):
        """
        从 url 后缀猜测文件扩展名
        :param url: 海报url
        """
        ext_map = {
            'jpg': '.jpg',
            'jpeg': '.jpg',
            'png': '.png',
            'webp': '.webp',
            'gif': '.gif',
            'bmp': '.bmp',
            'svg': '.svg',
            'ico': '.ico',
            'avif': '.avif',
        }
        # 获取海报 url 后缀名
        list_url = url.split('.')[-1].lower()
        for suffix in ext_map:
            if suffix in list_url:
                return ext_map.get(suffix, '.jpg')
        return '.jpg'

    # 并发函数
    @logger
    async def download_image(self, title, url, i, resp, headers, save_doc, **kwargs):
        """
        并发下载海报到文件夹
        :param title: 海报名称
        :param url: 海报 url
        :param i: 下载的海报的顺序数 - 1
        :param resp: 用于请求的 client
        :param headers: 请求头
        :param save_doc: 储存文件的文件夹
        :param kwargs: logger(供 @logger 使用)
        :return: file_path, image_bytes
        """
        await asyncio.sleep(random.uniform(0, 1))  # 0~1秒之间的随机抖动
        self.logger.info(f"---已将第 {i + 1} 张海报的 URL 加入爬取队列---")

        # 获取海报url
        poster_url = url
        if not poster_url or not poster_url.strip():
            return f"第 {i + 1} 张海报的 URL 无效, 跳过"
        else:
            try:
                # 获取海报图像二进制数据, Content-Type
                image_bytes, content_type = await resp.request_poster_url(poster_url, headers=headers, logger=self.logger)
                # 获取中文名
                poster_name = title
                # 检查 Content-Type 是否以 image/ 开头
                if not content_type.startswith('image/'):
                    return f"海报名称: {poster_name} | 返回内容不是图片: {content_type}"
                # 检查内容长度
                elif len(image_bytes) == 0:
                    return f"海报名称: {poster_name} | 返回内容为空"
                # 获取完整路径
                pic_extension = self._guess_extension(poster_url)
                file_path = os.path.join(save_doc, poster_name + pic_extension)
                self.logger.info(f"✅成功获取第 {i + 1} 张海报的二进制数据")
                return file_path, image_bytes
            except Exception as e:
                self.logger.error(f"❌第 {i + 1} 张海报: {type(e).__name__}: {e}")
                raise e

    # 保存海报
    @logger
    async def save_to_document(self, save_doc, key_message, headers, cookies, **kwargs) -> None:
        """
        将海报保存到文件夹
        :param save_doc: 储存文件的文件夹
        :param key_message: 目标网站关键词
        :param headers: 请求头
        :param cookies: 所需的 cookies
        :param kwargs: logger(供 @logger 使用)
        """
        async with Poster(cookies=cookies, logger=self.logger) as resp:
            poster_obj = MoviePosterCrawler(self.logger)
            # 获取 title 和 poster_url
            ori_data = await poster_obj.fetch_page(resp, key_message, headers=headers, logger=self.logger)
            # 自动创建文件夹
            os.makedirs(save_doc, exist_ok=True)

            # 创建 poster_url 字典
            poster_url_list = [(movie.title, movie.poster_url) for movie in ori_data]

            # 创建并发任务
            tasks = [
                self.download_image(title, url, i, resp, headers, save_doc, logger=self.logger)
                for i, (title, url) in enumerate(poster_url_list)
            ]
            # 执行并发任务
            poster_list = await asyncio.gather(*tasks)
            i = 0
            for result in poster_list:
                i += 1
                if isinstance(result, tuple):
                    file_path, image_bytes = result
                    with open(file_path, 'wb') as f:
                        f.write(image_bytes)
                    self.logger.info(f"✅成功将第 {i} 张海报保存到文件夹, file_path: {file_path}")
                else:
                    # result 可能为 None 或 str(具体错误信息)
                    self.logger.warning(f"第 {i} 张海报下载失败: {result}")

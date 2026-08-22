from movie import logging_configuration

from crawler import MovieRatingCrawler
from pipeline import SaveData
from models import MovieRatingCrawlerConfig

import asyncio


async def main(config: MovieRatingCrawlerConfig):
    # 创建 logger
    logger = logging_configuration(config.logger_name, config.logger_file_path)
    # 创建爬取类实例
    crawler_obj = MovieRatingCrawler(config, logger=logger)
    # 设置请求头
    _headers = config.headers

    logger.info("\n------开始爬取标题和评分数据------")

    try:
        data = await crawler_obj.fetch_page(config.key_message, _headers, logger=logger)
        try:
            save_obj = SaveData(data, config.storage_path, logger=logger)
            save_obj.save_to_json()
        except Exception as e:
            logger.error(f"❌SaveData | {type(e).__name__}: {e}")
            raise e
    except Exception as e:
        logger.error(f"❌MovieRatingCrawler | {type(e).__name__}: {e}")
        raise e


if __name__ == "__main__":
    headers={}
    crawler_config = MovieRatingCrawlerConfig(
        start_url='',
        headers=headers,
        key_message='',
        logger_name='',
        logger_file_path='',
        storage_path='',
        movie_item_selector='',
        title_selector='',
        rating_selector='',
        next_url_selector='',
        next_url_attribute=''
    )
    asyncio.run(main(crawler_config))
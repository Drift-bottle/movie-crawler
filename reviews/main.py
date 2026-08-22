from movie import logging_configuration, get_position_with_edge_login
from crawler import MovieReviewCrawler
from pipeline import SaveData
from models import ReviewsCrawlerConfig
import asyncio


async def main(config: ReviewsCrawlerConfig):
    # 获取 logger
    logger = logging_configuration(config.logger_name, config.logger_file_path)

    logger.info("\n------开始获取 cookies------")

    target_domains = config.target_domains
    cookies = await get_position_with_edge_login(target_domains, cookies_logger=logger, logger=logger)
    # 获取 headers
    _headers = config.headers
    # 创建爬取类实例
    crawler_obj = MovieReviewCrawler(cookies, config, logger=logger)

    logger.info("\n------开始爬取短评和评分数据------")

    try:
        data = await crawler_obj.fetch_page(config.key_message, _headers, logger=logger)
        try:
            save_obj = SaveData(data, logger=logger)
            save_obj.save_to_csv(config.origin_file_path, config.static_file_path)
        except Exception as e:
            logger.error(f"❌SaveData | {type(e).__name__}: {e}")
            raise e
    except Exception as e:
        logger.error(f"❌MovieReviewCrawler | {type(e).__name__}: {e}")
        raise e

if __name__ == "__main__":
    headers = {}
    crawler_config = ReviewsCrawlerConfig(
        start_url='',
        headers=headers,
        key_message='',
        logger_name='',
        logger_file_path='',
        origin_file_path='',
        static_file_path='',
        target_domains=[''],
        review_item_selector='',
        rating_selector='',
        rating_attribute='',
        content_selector='',
        next_url_selector='',
        next_url_attribute='',
    )
    asyncio.run(main(crawler_config))
from movie import logging_configuration, get_position_with_edge_login
from pipeline import SaveData
from models import PosterCrawlerConfig
import asyncio


async def main(config: PosterCrawlerConfig):
    # 获取 logger
    logger = logging_configuration(config.logger_name, config.logger_file_path)

    logger.info("\n------开始获取 cookies------")

    target_domains = config.target_domains
    cookies = await get_position_with_edge_login(target_domains ,logger=logger, cookies_logger=logger)
    # 获取 headers
    _headers = config.headers
    # 创建 SaveData 实例
    data_obj = SaveData(logger=logger)

    logger.info("\n------开始爬取标题和海报数据------")

    try:
        await data_obj.save_to_document(
            config.storage_path,
            config.key_message,
            _headers,
            config,
            cookies,
            logger=logger
        )
    except Exception as e:
        logger.error(f"❌SaveData | {type(e).__name__}: {e}")
        raise e


if __name__ == '__main__':
    crawler_config = PosterCrawlerConfig(
        start_url='',
        headers={},
        key_message='',
        logger_name='',
        logger_file_path='',
        target_domains=[''],
        storage_path='',
        movie_item_selector='',
        title_selector='',
        poster_url_selector='',
        poster_url_attribute='',
        next_url_selector='',
        next_url_attribute=''
    )
    asyncio.run(main(crawler_config))
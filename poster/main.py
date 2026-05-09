from movie.utils import logging_configuration, get_position_with_edge_login
from pipelines import SaveData
import asyncio


async def main():
    # 获取 logger
    logger = logging_configuration('poster_logger', 'movie_poster.log')

    logger.info("\n------开始获取 cookies------")

    target_domains = ['...', ]
    cookies = await get_position_with_edge_login(target_domains ,logger=logger, cookies_logger=logger)
    # 获取 headers
    headers = {
        'User-Agent': '',
        'Accept': '',
        'Accept-Language': ''
    }
    # 创建 SaveData 实例
    data_obj = SaveData(logger=logger)

    logger.info("\n------开始爬取标题和海报数据------")

    try:
        await data_obj.save_to_document(r'...', 'key_message', headers, cookies, logger=logger)
    except Exception as e:
        logger.error(f"❌SaveData | {type(e).__name__}: {e}")
        raise e

if __name__ == '__main__':
    asyncio.run(main())
from movie.utils import logging_configuration, get_position_with_edge_login
from crawler import MovieReviewCrawler
from pipeline import SaveData
import asyncio


async def main():
    # 获取 logger
    logger = logging_configuration('review_logger', 'movie_reviews.log')

    logger.info("\n------开始获取 cookies------")

    target_domains = ['',]
    cookies = await get_position_with_edge_login(target_domains, cookies_logger=logger)
    # 获取 headers
    headers = {
        'User-Agent': '',
        'Accept': '',
        'Accept-Language': '',
        'Referer': ''
    }
    # 创建爬取类实例
    crawler_obj = MovieReviewCrawler(cookies=cookies, logger=logger)

    logger.info("\n------开始爬取短评和评分数据------")

    try:
        data = await crawler_obj.fetch_page("key_message", headers=headers, logger=logger)
        try:
            save_obj = SaveData(data, logger=logger)
            save_obj.save_to_csv('movie_reviews.csv', 'static_outcome.csv', 'D:\\')
        except Exception as e:
            logger.error(f"❌SaveData | {type(e).__name__}: {e}")
            raise e
    except Exception as e:
        logger.error(f"❌MovieReviewCrawler | {type(e).__name__}: {e}")
        raise e

if __name__ == "__main__":
    asyncio.run(main())
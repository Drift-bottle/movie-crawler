from crawler import MovieRatingCrawler
from pipeline import SaveData
from movie.utils import logging_configuration
import asyncio


if __name__ == '__main__':
    # 创建 logger
    logger = logging_configuration('title_rating', 'title_rating.log')
    # 创建爬取类实例
    crawler_obj = MovieRatingCrawler(logger)
    # 设置请求头
    _headers = {
        'User-Agent': '...',
        'Accept': '...',
        'Accept-Language': '...'
    }

    logger.info("\n------开始爬取标题和评分数据------")

    try:
        data = asyncio.run(crawler_obj.fetch_page("key_message", headers=_headers, logger=logger))
        try:
            save_obj = SaveData(data, r"D:\movie-crawler\storage\movie_title_rating.json", logger)
            save_obj.save_to_json()
        except Exception as e:
            logger.error(f"❌SaveData | {type(e).__name__}: {e}")
            raise e
    except Exception as e:
        logger.error(f"❌MovieRatingCrawler | {type(e).__name__}: {e}")
        raise e

"""
movie_poster: 电影海报数据抓取与下载子包。

提供电影海报 URL 的抓取、解析，以及海报图片的并发下载与存储功能。
"""

from .crawler import Poster, MoviePosterCrawler
from .pipeline import SaveData
from .models import PosterUrl, PosterCrawlerConfig

__all__ = [
    "Poster",
    "MoviePosterCrawler",
    "SaveData",
    "PosterUrl",
    "PosterCrawlerConfig",
]
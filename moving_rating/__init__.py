"""
movie_rating: 电影评分数据抓取与存储子包。

提供电影评分数据的抓取、解析和 JSON 存储功能。
"""

from .crawler import MovieRatingCrawler
from .pipeline import SaveData
from .models import MovieRating, MovieRatingCrawlerConfig

__all__ = [
    "MovieRatingCrawler",
    "SaveData",
    "MovieRating",
    "MovieRatingCrawlerConfig",
]
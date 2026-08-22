"""
movie_review: 电影短评与评分数据抓取、存储及统计分析子包。

提供电影短评和评分数据的抓取、解析，以及 CSV 存储与评分分布统计功能。
"""

from .crawler import MovieReviewCrawler
from .pipeline import SaveData
from .models import MovieReview, ReviewsCrawlerConfig

__all__ = [
    "MovieReviewCrawler",
    "SaveData",
    "MovieReview",
ReviewsCrawlerConfig
]
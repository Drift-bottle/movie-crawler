from dataclasses import dataclass, asdict

@dataclass
class MovieRating:
    """电影评分数据"""
    title: str # 电影标题
    rating: str # 电影评分

    def to_dict(self):
        return asdict(self)

@dataclass
class MovieRatingCrawlerConfig:
    """爬虫配置"""
    start_url: str

    headers: dict
    key_message: str

    logger_name: str
    logger_file_path: str

    storage_path: str

    movie_item_selector: str
    title_selector: str
    rating_selector: str
    next_url_selector: str

    # 属性（职位详情页链接）
    next_url_attribute: str
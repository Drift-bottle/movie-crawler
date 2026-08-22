from dataclasses import dataclass, asdict

@dataclass
class MovieReview:
    """电影短评数据"""
    rating: str # 短评评分
    review: str # 电影短评

    def to_dict(self):
        return asdict(self)

@dataclass
class ReviewsCrawlerConfig:
    """爬虫配置"""
    start_url: str

    headers: dict
    key_message: str

    logger_name: str
    logger_file_path: str

    origin_file_path: str
    static_file_path: str

    target_domains: list

    review_item_selector: str
    rating_selector: str
    rating_attribute: str
    content_selector: str
    next_url_selector: str

    # 属性（职位详情页链接）
    next_url_attribute: str
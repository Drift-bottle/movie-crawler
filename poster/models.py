from dataclasses import dataclass

@dataclass
class PosterUrl:
    """电影海报url数据"""
    title: str # 电影标题
    poster_url: str # 海报url

@dataclass
class PosterCrawlerConfig:
    """爬虫配置"""
    start_url: str
    headers: dict
    key_message: str

    logger_name: str
    logger_file_path: str

    target_domains: list

    storage_path: str

    movie_item_selector: str
    title_selector: str
    poster_url_selector: str
    poster_url_attribute: str

    next_url_selector: str
    # 属性（职位详情页链接）
    next_url_attribute: str
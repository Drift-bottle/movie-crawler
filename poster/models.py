from dataclasses import dataclass

@dataclass
class PosterUrl:
    """电影海报url数据"""
    title: str # 电影标题
    poster_url: str # 海报url
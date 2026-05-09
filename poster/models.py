from dataclasses import dataclass, asdict

@dataclass
class PosterUrl:
    """电影海报url数据"""
    title: str # 电影标题
    poster_url: str # 海报url

    def to_dict(self):
        return asdict(self)
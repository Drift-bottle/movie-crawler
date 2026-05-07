from dataclasses import dataclass, asdict

@dataclass
class MovieRating:
    """电影评分数据"""
    title: str # 电影标题
    rating: str # 电影评分

    def to_dict(self):
        return asdict(self)

from dataclasses import dataclass, asdict

@dataclass
class MovieReview:
    """电影短评数据"""
    rating: str # 短评评分
    review: str # 电影短评

    def to_dict(self):
        return asdict(self)
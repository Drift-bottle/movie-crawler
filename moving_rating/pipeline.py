import json
import os
import logging
from typing import List, Any


class SaveData:
    """保存解析后的数据"""
    def __init__(self, data: List[Any], filepath: str, logger=None):
        self.data = data # 解析后的数据
        self.filepath = filepath # 储存 json 数据的完整路径
        self.logger = logger or logging.getLogger(__name__) # 设置logger

    def save_to_json(self) -> None:
        """将数据储存到json文件中"""
        if len(self.data) == 0:
            err = "❌没有储存到数据"
            self.logger.error(err)
            raise Exception(err)
        movie_dict = [movie.to_dict() if hasattr(movie, 'to_dict') else movie for movie in self.data]
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(movie_dict, f, ensure_ascii=False, indent=4)
        if self.json_data_is_not_empty(self.filepath):
            self.logger.info(f"✅数据已储存到{self.filepath}")
        else:
            err = f"❌数据未储存到{self.filepath}"
            self.logger.error(err)

    def json_data_is_not_empty(self, filepath):
        """判断文件是否成功存入数据"""
        if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
            return False
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                self.logger.error(f"❌加载文件出问题 | {type(e).__name__}: {e}, 可能不是合法的 JSON")
                return False
        # 检查'无数据'形态
        if data is None:
            return False
        elif isinstance(data, (dict, list, str)):
            if data is str and len(data.strip()) > 0:
                return True
            elif len(data) > 0:
                return True
            else:
                return False
        # 其他类型(数字、布尔值等)通常视为"有数据"
        return True
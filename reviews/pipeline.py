import logging
import pandas as pd
import csv
import os


class SaveData:
    """保存解析后的短评数据"""
    def __init__(self, data, logger=None):
        self.data = data # 解析后的数据
        self.logger = logger or logging.getLogger(__name__) # 设置 logger

    def _row_generator(self):
        """逐个转换解析后的短评数据"""
        for movie in self.data:
            yield movie.to_dict() if hasattr(movie, 'to_dict') else movie

    def is_csv_has_data(self, filepath):
        """
        判断是否存入 csv 文件
        :param filepath: 指定的保存到的文件路径
        """
        if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
            return False
        try:
            df = pd.read_csv(filepath)
        except pd.errors.EmptyDataError as e:
            self.logger.error(f"❌加载 csv 数据失败, 异常: {e}")
            return False
        return not df.empty

    def save_to_csv(self, origin_file, static_file, filepath_start) -> None :
        """
        将数据储存到CSV文件中 | 进行评分统计
        :param origin_file: 保存转换后的初始数据的 csv 文件
        :param static_file: 保存统计结果的 csv 文件
        :param filepath_start: 指定的保存到的文件路径的开头(eg: 'D:\\')
        """
        if len(self.data) == 0:
            err = "❌ 未爬取到任何数据"
            self.logger.error(err)
            raise Exception(err)

        # 设置 origin_file 路径
        origin_path = os.path.join(filepath_start, 'movie-crawler', 'storage', origin_file)
        # 将转换后的初始数据保存到 csv
        with open(origin_path, 'w', newline='', encoding='utf-8') as f:
            # 获取表头
            fieldnames = list(self.data[0].to_dict().keys())
            # 将字典形式的数据写入文件
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            # 写入表头
            writer.writeheader()
            # 一边取数据一边写文件
            writer.writerows(self._row_generator())

        if self.is_csv_has_data(origin_path):
            self.logger.info(f"✅已成功将数据储存到 {origin_path}")

            # 读取csv文件
            df = pd.read_csv(origin_path)
            # 统计评分分布
            counts_df = df['rating'].value_counts()
            # 将counts_df转化成Dataframe并重置索引
            result = counts_df.reset_index()
            # 定义表头
            result.columns = ['rating', 'score']
            # 计算百分比
            result['percentage'] = result['score'] / result['score'].sum()
            # 将百分比转换成 %形式
            result['percentage_str'] = result['percentage'].apply(lambda x: f'{x:.1%}')

            # 设置 static_file 路径
            static_path = os.path.join(filepath_start, 'movie-crawler', 'storage' ,static_file)
            # 将统计结果保存到 csv
            with open(static_path, 'w', newline='', encoding='utf-8') as f:
                result.to_csv(f, index=False)
            if self.is_csv_has_data(static_path):
                self.logger.info(f"✅已成功将数据储存到 {static_path}")
            else:
                self.logger.error(f"❌{static_path}中没有数据")
        else:
            self.logger.error(f"❌{origin_path}中没有数据")
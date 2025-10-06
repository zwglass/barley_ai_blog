import sys
from pathlib import Path

project_path = Path(__file__).resolve().parent.parent
sys.path.append(str(project_path))

from confs.glob_configs import SingletonGlobConfs     # 全局配置类
from zwutils_methods import GoodsSetPath    # 商品路径


class MainParams(object):
    """
    from main_params import  MainParams      # 操作的文件夹,统一入口; 修改 main_params.py 的参数.
    #    cls_main_params = MainParams()      # 操作的文件夹,统一入口; 修改 main_params.py 的参数.
    """
    def __init__(self):
        self.glob_confs  = SingletonGlobConfs()     # 全局配置类
        self.cls_goodset_path = GoodsSetPath()    # 商品路径

        # 视频裁剪尺寸
        self.crop_width = None      # 宽度 1080  如果crop_width==None 裁剪为正方型
        self.crop_height = 1080     # 高度 1080  如果crop_width==None 裁剪为正方型
        self.crop_position = None     # 视频裁剪左上脚坐标 None 居中裁剪; (0, 0): (x轴, y轴);

        self.handle_year = None    # 文件夹按年分类 (可以指定年份，如: y2025,  None 使用当前年份)
        self.date_prefix = None          # 文件夹日期(可以指定日期，如: 'd216', None 使用当前日期)
        self.init_goods_dirs_paths()

    def init_goods_dirs_paths(self):
        # 初始化所有商品文件夹路径
        self.handle_year, self.date_prefix = self.cls_goodset_path.compute_handle_year_and_day(self.handle_year, self.date_prefix)


        
cls_main_params = MainParams()      # 操作的文件夹,统一入口; 修改 main_params.py 的参数.
# from main_params import cls_main_params      # 操作的文件夹,统一入口; 修改 main_terminal_params.py 的参数.

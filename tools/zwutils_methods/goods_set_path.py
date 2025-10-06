import os
import datetime
import pytz     # pip install pytz
import shutil
from pathlib import Path
from typing import Tuple


class GoodsSetPath(object):
    """
    from zwutils_methods import GoodsSetPath    # 商品路径
    #    self.cls_goodset_path = GoodsSetPath()    # 商品路径

    # 商品文件夹按日放到同一个文夹内 (新的文件归类) version: 1.0
    """
    def __init__(self):
        pass

    def today_year_month_day(self):
        """
        获取当天 年月日 (北京时间)
        """
        current_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
        # 格式化输出：年-月（2位）-日（2位）
        # formatted_date = current_time.strftime("%Y-%m-%d")

        # print(f"年：{current_time.year}, 月：{current_time.month:02d}, 日：{current_time.day:02d}")
        return f"{current_time.year}", f"{current_time.month:02d}", f"{current_time.day:02d}"

    def compute_day_dir_name(self, goods_type:str, date_prefix=None) -> str:
        # 计算一天的商品文件夹名称
        y, m, d = self.today_year_month_day()
        m = m[1:] if m.startswith('0') else m

        ds = date_prefix if date_prefix is not None else f'd{m}{d}'
        day_dir_name = f'{self.dir_prefix_dict[goods_type]}_{ds}'
        return day_dir_name
        
    def compute_handle_year_and_day(self, handle_year=None, date_prefix=None):
        # 计算 操作的年 和天
        y, m, d = self.today_year_month_day()
        ret_y = f"y{y}" if handle_year is None else handle_year
        m = m[1:] if m.startswith('0') else m
        ret_date_prefix = date_prefix if date_prefix is not None else f'd{m}{d}'
        return ret_y, ret_date_prefix
    
    def compute_goods_type_from_dir_prifix(self, goods_dir_name:str) -> str:
        # 由商品文件夹名计算商品分类的名称
        dir_prefix = goods_dir_name.split('_')[0]
        for k, v in self.dir_prefix_dict.items():
            if v == dir_prefix:
                return k
        return None
    
    def check_goods_dir(self, dir_prefix:str, path_obj_goods:Path) -> bool:
        # 判断是否是商品目录 ---* 同一天商品放当前文件夹 *---
        is_goods_dir_path = True
        if not path_obj_goods.is_dir() or not path_obj_goods.name.startswith(dir_prefix) or path_obj_goods.name.endswith('_resized') or path_obj_goods.name.endswith('_'):
            is_goods_dir_path = False
        return is_goods_dir_path
    
    def check_dispense_glasses_dir(self, goods_dir_path:str):
        # 验证是否是配镜商品 版本号 m 开头(例如: m2501)
        goods_dir_name_splited = Path(goods_dir_path).stem.split('_')
        return len(goods_dir_name_splited) == 4 and goods_dir_name_splited[2].startswith('m')
    
    def goods_dir_to_dispense_name(self, goods_dir_name:str) -> str | None:
        # 商品文件夹转 配镜文件夹名
        goods_dir_name_splited = goods_dir_name.split('_')
        if len(goods_dir_name_splited) == 4:
            goods_dir_dispense_name = f'{goods_dir_name_splited[0]}_{goods_dir_name_splited[1]}_m{goods_dir_name_splited[2][1:]}_{goods_dir_name_splited[3]}'
            return goods_dir_dispense_name
        else:
            return None
    
    def compute_goods_dir_name_with_detail_img_path(self, detail_img_path) -> Tuple[str, str]:
        # 根据detail 图片路径 计算商品文件夹名和图片名
        img_name = Path(detail_img_path).name
        goods_dir_name = Path(detail_img_path).parent.parent.name
        return goods_dir_name, img_name

    def compute_goods_dir_name_with_goodstype_version_series(self, goods_type:str, version:str, series:str, date_str:str=None) -> str:
        # 根据 goods_type, version, series  计算商品文件夹名; 
        # series: 可以是型号, 或系列
        # date_str='d807' | None
        y, m, d = self.today_year_month_day()
        m = m[1:] if m.startswith('0') else m

        ds = date_str if date_str is not None else f'd{m}{d}'
        prefix = self.dir_prefix_dict[goods_type]
        goods_dir_name = f'{prefix}_{ds}_{version}_{series.lower()}'
        return goods_dir_name
    
    def compute_detail_img_path(self, detail_img_name, goods_dir_path) -> str:
        # 计算详情图片路径
        img_path = Path(goods_dir_path) / 'details' / detail_img_name
        return str(img_path)
    
    def compute_goods_object_bg_imgs_path(self, goods_path, object_img_name=None, bg_img_name=None):
        # 计算商品和背景图片的路径
        # object_img_name, bg_img_name 可以带后缀，也可不带后缀
        details_dir_path = str(Path(goods_path) / 'details')
        object_img_name_stem, bg_img_name_stem = None, None
        if object_img_name is not None:
            object_img_name_stem = Path(object_img_name).stem
        if bg_img_name is not None:
            bg_img_name_stem = Path(bg_img_name).stem

        object_img_path, bg_img_path = None, None

        all_details_imgs = self.get_imgs_paths_in_dir(folder_path=details_dir_path, prefix=('d_91', 'd_92', ))
        for d_path in all_details_imgs:
            d_path_stem = Path(d_path).stem
            if object_img_name_stem is not None:
                if d_path_stem == object_img_name_stem:
                    object_img_path = d_path
            else:
                if d_path_stem.startswith('d_91'):
                    object_img_path = d_path

            if bg_img_name_stem is not None:
                if d_path_stem == bg_img_name_stem:
                    bg_img_path = d_path
            else:
                if d_path_stem.startswith('d_92'):
                    bg_img_path = d_path

            if object_img_path is not None and bg_img_path is not None:
                break
        return object_img_path, bg_img_path
    
    def compute_goods_gimp_base_imgs_paths(self, goods_path, base_imgs_names = None) -> list:
        # 计算基础图片的路径 
        # base_imgs_names==None 全部 d_8 开头的图片路径; 否则d_8开头的路径筛选包含 base_imgs_names 的图片 
        ret_imgs_paths = []
        details_dir_path = str(Path(goods_path) / 'details')
        all_d8_imgs = self.get_imgs_paths_in_dir(folder_path=details_dir_path, prefix=('d_8', ))
        if base_imgs_names is not None:
            ret_imgs_paths = [img_path for img_path in all_d8_imgs if Path(img_path).name in base_imgs_names or Path(img_path).stem in base_imgs_names]
            return ret_imgs_paths
        else:
            return all_d8_imgs

    def get_imgs_paths_in_dir(self, folder_path, prefix=None):
        '''
        获取指定目录下的所有图片路径
        :param dir_path: 图片所在的目录
        :return: list
        '''
        # 检查文件夹是否存在且是一个目录
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            raise FileNotFoundError(f"The specified folder does not exist. ({folder_path})")
        
        image_paths = []
        
        # 遍历文件夹中的每一个文件和子目录
        for filename in os.listdir(folder_path):
            if prefix is not None and not filename.startswith(prefix):
                continue

            file_path = os.path.join(folder_path, filename)
            
            # 确保处理的是文件而不是子目录
            if os.path.isfile(file_path):
                ext = os.path.splitext(filename)[1].lower()  # 获取扩展名并转为小写
                
                # 检查是否是JPG或PNG格式
                if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                    image_paths.append(file_path)
        
        # 对路径列表进行排序
        image_paths.sort()
        
        return image_paths


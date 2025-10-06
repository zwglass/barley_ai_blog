from pathlib import Path
import threading
import os
import re


"""
from confs.glob_configs import SingletonGlobConfs     # 全局配置类
# self.glob_confs  = SingletonGlobConfs()     # 全局配置类
"""

class SingletonGlobConfs(object):
    _instance = None
    _lock = threading.Lock()  # 用于保护实例创建的锁

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("Creating new instance")
            cls._instance = super().__new__(cls)
            # 这里调用实例方法
            path_project_dir = Path(__file__).resolve().parent.parent.parent
            path_tools_dir = path_project_dir / 'tools'
            path_tmp_dir = path_tools_dir / 'tmps'
            path_tmp_dir.mkdir(parents=True, exist_ok=True)
            font_path_hansans = path_tools_dir / 'confs' / 'fonts_zh' / 'SourceHanSansSCVF.ttf'    # 思源细体 广告字
            font_path_hansans_hw = path_tools_dir / 'confs' / 'fonts_zh' / 'SourceHanSansHWSCVF.ttf'    # 思源黑体 广告字

            cls._instance._configs = {
                'path_project': str(path_project_dir),
                'path_tools_dir': str(path_tools_dir),
                'path_tmp_dir': str(path_tmp_dir),
                'font_path_hansans': str(font_path_hansans),    # 思源细体 广告字
                'font_path_hansans_hw': str(font_path_hansans_hw),    # 思源黑体 广告字
            }
        # else:
        #     # print("Returning existing instance")
        return cls._instance

    def __new__(cls):
        return cls.get_instance()
    
    def set_config(self, key, value):
        """设置配置项"""
        with self._lock:
            self._configs[key] = value

    def get_config(self, key):
        """获取配置项，如果键不存在则返回 None"""
        with self._lock:
            return self._configs.get(key, None)

    def delete_config(self, key):
        """删除配置项"""
        with self._lock:
            if key in self._configs:
                del self._configs[key]

    def get_comfyui_api_prompts_path(self, prompt_name:str) -> str:
        # 计算comfyui_api_prompts json 文件的绝对路径
        dirpath_comfyui_api_prompts = self.get_config('dir_path_comfyui_api_prompts')
        if prompt_name.endswith('.json'):
            return os.path.join(dirpath_comfyui_api_prompts, prompt_name)
        else:
            return os.path.join(dirpath_comfyui_api_prompts, f'{prompt_name}.json')

    def compute_font(self, text):
        # 计算字体类型, 全中文 使用 font_path, 否则使用 font_path_roman;
        arrow_pattern = re.compile(
            r'[\u2190-\u2193\u2196-\u2199\u21A0-\u21A3\u21A6\u21A9\u21AA\u21B0-\u21B3'
            r'\u21B6\u21B7\u21BA\u21BB\u21C4\u21C6\u21C7\u21C9\u21CB-\u21CF'
            r'\u21D0-\u21D5\u21DA\u21DB\u21DD\u21E0-\u21E3\u21E6-\u21E9'
            r'\u21F0-\u21F3\u27F0-\u27FF\u2900-\u297F\u2B00-\u2B2F'
            r'\u2B45\u2B46\u2B4D-\u2B4F\u2B50-\u2B59\uFE10-\uFE19'
            r'\uFFE8-\uFFEE]'
        )
        include_arrow = bool(arrow_pattern.search(text))
        # print(include_arrow)
        if include_arrow:
            return self.get_config('font_path_menlo')
        else:
            return self.get_config('font_path')
        
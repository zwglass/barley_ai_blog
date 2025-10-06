import zipfile
import os
import json
from pathlib import Path
from datetime import datetime


class FileHandle(object):
    """
    from zwutils_methods import FileHandle        # 文件操作
    #    self.cls_file_handle = FileHandle()          # 文件操作
    """
    def __init__(self):
        pass

    def write_json_file(self, write_path, obj_data):
        # list dict 保存到文件
        try:
            with open(write_path, 'w', encoding='utf-8') as f:
                json.dump(obj_data, f, ensure_ascii=False, indent=4)
                # ensure_ascii=False: 允许非 ASCII 字符（如中文）正常显示
                # indent=4: 使输出的 JSON 文件有良好的缩进格式，便于阅读
            return True
        except Exception as e:
            print('Error write_json_file failed: ', e)
            return False
        
    def read_json_file(self, json_path):
        """
        读取并解析 JSON 文件
        参数:
            file_path (str): JSON 文件的完整路径
        返回:
            dict/list: 解析后的 Python 对象（字典或列表）
        异常:
            FileNotFoundError: 文件路径不存在或不是文件
            ValueError: 文件内容不是有效的 JSON 格式
            Exception: 其他读取错误
        """
        # 验证文件是否存在且是真实文件
        if not Path(json_path).is_file():
            raise FileNotFoundError(f"文件不存在: {json_path}")

        try:
            # 使用上下文管理器安全打开文件
            with open(json_path, 'r', encoding='utf-8') as f:
                try:
                    # 解析 JSON 内容
                    return json.load(f)
                except json.JSONDecodeError as e:
                    # 提供详细的 JSON 解析错误信息
                    error_msg = f"JSON 解析失败 ({json_path}): "
                    error_msg += f"行 {e.lineno} 列 {e.colno} - {e.msg}"
                    raise ValueError(error_msg) from e
        except UnicodeDecodeError:
            raise ValueError("编码错误: 请尝试使用正确的编码（如 'utf-8'）")
        except Exception as e:
            raise Exception(f"读取文件时发生未知错误: {str(e)}") from e
        
    def get_creation_time(self, file_path) -> int:
        # 获取文件创建时间戳; window mac 为文件创建时间, linux 是最后修改时间
        file_path_obj = Path(file_path)  # 替换为你的文件路径

        # 获取创建时间
        creation_timestamp = file_path_obj.stat().st_ctime
        return int(creation_timestamp)

    def zip_multiple_to_one(self, folders_list:list, output_zip_path:str):
        """将多个文件夹压缩到一个ZIP文件中"""
        # if zip_name is None:
        #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #     zip_name = f"combined_{timestamp}.zip"
        
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder_path in folders_list:
                if not os.path.exists(folder_path):
                    print(f"跳过不存在的文件夹: {folder_path}")
                    continue
                
                folder_name = os.path.basename(folder_path)
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join(folder_name, os.path.relpath(file_path, folder_path))
                        zipf.write(file_path, arcname)
        
        return output_zip_path
    
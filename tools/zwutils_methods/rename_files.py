import os
from pathlib import Path


class RenameFiles(object):
    """
    重命名文件 video_001.mp4 video_002.mp4 这样的格式连续命名
    from zwutils_methods import RenameFiles    # 重命名文件 video_001.mp4 video_002.mp4 这样的格式连续命名
    # self.cls_rename_files = RenameFiles()    # 重命名文件 video_001.mp4 video_002.mp4 这样的格式连续命名
    """

    def rename_files(self, prefix:str, files_path_list:list, padding=3):
        """
        重命名文件夹中的视频文件，如果不是以'video_'开头，则重命名为video_001.mp4格式
        
        参数:
            prefix: 文件前缀 比如: video_
            files_path_list (list): 文件路径
            padding: 数字部分的位数，默认为3（即001, 002...）
        """
        
        # 按文件名排序，确保重命名顺序一致
        files_path_list.sort()
        
        # 计数器，用于生成序号
        counter = 1
        
        for file_path in files_path_list:
            folder_path = Path(file_path).parent
            file_name = Path(file_path).name
            ext = Path(file_path).suffix       # 文件扩展名保存不变
            
            # 如果文件名已经以video_开头，跳过
            if file_name.lower().startswith(prefix) or not file_name.endswith(ext):
                print(f"跳过 '{file_name}' (已符合命名规则 或 非目标文件)")
                continue
            
            # 生成新文件名，格式为video_001.mp4
            new_filename = f"{prefix}{counter:0{padding}d}{ext}"
            new_path = str(folder_path / new_filename)
            
            # 确保新文件名不存在
            while os.path.exists(new_path):
                counter += 1
                new_filename = f"{prefix}{counter:0{padding}d}{ext}"
                new_path = str(folder_path / new_filename)
            
            # 重命名文件
            try:
                os.rename(file_path, new_path)
                print(f"重命名 '{file_name}' 为 '{new_filename}'")
                counter += 1
            except Exception as e:
                print(f"重命名 '{file_name}' 失败: {str(e)}")

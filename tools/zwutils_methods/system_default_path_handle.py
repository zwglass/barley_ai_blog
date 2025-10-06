import os


class SystemDefaultPathHandle():
    """
    系统默认路径获取
    from zwutils_methods import SystemDefaultPathHandle        # 系统默认路径获取
    # self.cls_systempath = SystemDefaultPathHandle()       # 系统默认路径获取
    """
    def __init__(self):
        pass

    def get_download_path(self):
        if os.name == 'nt':  # 检查是否为Windows系统
            return os.path.join(os.environ['USERPROFILE'], 'Downloads')
        else:                # macOS/Linux系统
            return os.path.join(os.path.expanduser('~'), 'Downloads')


if __name__ == '__main__':
    # cls_systempath = SystemDefaultPathHandle()        # 系统默认路径获取
    cls_systempath = SystemDefaultPathHandle()       # 系统默认路径获取
    download_folder = cls_systempath.get_download_path()
    print("下载文件夹路径:", download_folder)
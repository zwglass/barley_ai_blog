import os
import random


class RandomHandle(object):
    """
    from zwutils_methods import RandomHandle    # 随机选择类
    # self.cls_randomhandle = RandomHandle()    # 随机选择类 
    """
    def __init__(self):
        pass

    def select_random_files(self, folder_path, prefix, choose_num, shuffle_results=True):
        """
        随机选择文件夹中以指定字符串开头的两个文件。

        Args:
            folder_path: 文件夹路径。
            prefix: 文件名前缀字符串。

        Returns:
            包含两个随机选择的文件路径的列表，如果符合条件的文件少于两个，则返回 None。
        """

        matching_files = []
        for filename in os.listdir(folder_path):
            if filename.startswith(prefix):
                matching_files.append(os.path.join(folder_path, filename))

        if len(matching_files) < choose_num:
            return matching_files  # 符合条件的文件少于两个

        ret_files = random.sample(matching_files, choose_num)
        if shuffle_results:
            random.shuffle(ret_files)  # 打乱选择的文件列表
        return ret_files
    
    def random_choice(self, my_list):
        """
        从一个列表中随机选择一个元素。

        Args:
            my_list: 一个列表。

        Returns:
            列表中的一个随机元素。如果列表为空，则返回 None。
        """
        if not my_list:  # 检查列表是否为空
            return None
        return random.choice(my_list)
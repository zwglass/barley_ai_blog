import uuid
import time


class DefaultValue(object):
    """
    from zwutils_methods import DefaultValue
    """
    def unique_url_string(self, length=16):
        # 生成UUID字符串并截取指定长度
        unique_id = str(uuid.uuid4()).replace('-', '').lower()
        # 去掉UUID中的横杠并截取前N个字符
        return unique_id[:length]
    
    def rowid(self):
        return self.unique_url_string(length=16)
    
    def current_timestamp(self):
        # 获取当前时间戳
        return int(time.time())

import datetime
from dateutil.relativedelta import relativedelta
import pytz     # pip install pytz
# from django.utils.timezone import utc
# datetime.datetime.now(tz=timezone.utc) # you can use this value


class GetDateTime(object):
    """
    获取时间类
    所有时间都是 time_zone=utc, 查询时 django 会自动转换为北京时间
    from zwutils_methods import GetDateTime      # 获取时间类
    #    self.cls_getdatetime = GetDateTime()      # 获取时间类
    """
    def get_current_datetime(self) -> datetime.datetime:
        """
        获取当前时间
        """
        # return datetime.datetime.now(tz=timezone.utc)
        # utcnow_datetime = datetime.datetime.utcnow()
        # utcnow_datetime.replace(tzinfo=utc)
        return datetime.datetime.now()      # 获取电脑的系统时间

    def add_current_datetime(self, add_days=0, add_seconds=0, add_minutes=0, add_hours=0, add_weeks=0):
        """
        获取当前时间 加减 后的时间 # weeks=add_weeks
        """
        nt = self.get_current_datetime()
        return nt + datetime.timedelta(
                days=add_days,
                seconds=add_seconds,
                minutes=add_minutes,
                hours=add_hours,
                weeks=add_weeks
            )

    def get_today_zero_time(self):
        """
        获取当天 0 点的时间
        """
        nt = self.get_current_datetime()
        return nt - datetime.timedelta(hours=nt.hour, minutes=nt.minute, seconds=nt.second, microseconds=nt.microsecond)
    
    def get_today_zero_timestamp(self):
        """
        获取当天 0 点的时间戳
        """
        zero_time = self.get_today_zero_time()
        zero_timestamp = zero_time.timestamp()
        return int(zero_timestamp)
    
    def today_year_month_day(self):
        """
        获取当天 年月日 (北京时间)
        """
        current_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
        # 格式化输出：年-月（2位）-日（2位）
        formatted_date = current_time.strftime("%Y-%m-%d")

        # print(f"年：{current_time.year}, 月：{current_time.month:02d}, 日：{current_time.day:02d}")
        return f"{current_time.year}", f"{current_time.month:02d}", f"{current_time.day:02d}"


class ConvertDatetime(object):
    """
    日期时间转换类
    # self.cls_convert_datetime = ConvertDatetime()       # 日期时间转换类
    """
    def __init__(self):
        self.default_datetime_format_string = '%Y-%m-%d %H:%M:%S'

    def datetime_add_hours(self, add_hours, wait_add_datetime=datetime.datetime.now()):
        """
        时间加小时
        :param add_hours: 要增加的小时数
        :param wait_add_datetime:
        :return:
        """
        if isinstance(wait_add_datetime, str):
            # 如果是字符串先转为datetime
            convert_datetime = datetime.datetime.strptime(wait_add_datetime, '%Y-%m-%d %H:%M:%S')
        else:
            convert_datetime = wait_add_datetime
        add_datetime = datetime.timedelta(hours=int(add_hours))

        return convert_datetime + add_datetime
    
    def add_to_datetime(self, dt, days=0, months=0, years=0):
        """
        向datetime对象添加指定的天、月、年
        
        Args:
            dt: datetime.datetime对象
            days: 要添加的天数
            months: 要添加的月数
            years: 要添加的年数
        
        Returns:
            datetime.datetime对象
        """
        # 先添加年、月（使用relativedelta处理月份和年份的加减）
        result = dt + relativedelta(years=years, months=months)
        
        # 再添加天数（使用timedelta）
        result += datetime.timedelta(days=days)
        
        return result

    def datetime_add_minutes(self, add_minutes, wait_add_datetime=datetime.datetime.now()):
        """
        时间加分钟
        :param add_minutes: 要增加的分钟数
        :param wait_add_datetime:
        :return:
        """
        if isinstance(wait_add_datetime, str):
            # 如果是字符串先转为datetime
            convert_datetime = datetime.datetime.strptime(wait_add_datetime, '%Y-%m-%d %H:%M:%S')
        else:
            convert_datetime = wait_add_datetime
        add_datetime = datetime.timedelta(minutes=int(add_minutes))

        return convert_datetime + add_datetime
    
    def ymd_str2datetime(self, ymd_str) -> datetime.datetime | None:
        """
        天字符串 转换为时间 datetime
        :param ymd_str: 例如 2025-09-15
        :return: datetime.datetime | None
        """
        try:
            # print('datetime_handle 50: now time: ', datetime.datetime.now())
            local_format = '%Y-%m-%d'
            ret = datetime.datetime.strptime(ymd_str, local_format)
            # print('datetime_handle 55: datetime: ', type(ret), ret)
            return ret
        except Exception as e:
            print('datetime_handle 58: datetime: ', e)
            return None

    def t_string_to_datetime(self, source_datetime_str):
        """
        时间字符串包含 T 转换为时间 datetime
        :param source_datetime_str: 例如 2019-11-21T10:04:01.234457+08:00
        :return:
        """
        try:
            # print('datetime_handle 50: now time: ', datetime.datetime.now())
            local_format = '%Y-%m-%dT%H:%M:%S'
            list1 = source_datetime_str.split('.')
            convert_str = list1[0]
            ret = datetime.datetime.strptime(convert_str, local_format)
            # print('datetime_handle 55: datetime: ', type(ret), ret)
            return ret
        except Exception as e:
            print('datetime_handle 58: datetime: ', e)
            return None

    def datetime_format_string(self, wait_convert_datetime: datetime.datetime, format_str=''):
        """
        datetime 格式化字符串
        :param wait_convert_datetime:
        :param format_str:
        :return:
        """
        use_format_str = format_str if len(format_str) > 0 else self.default_datetime_format_string
        return wait_convert_datetime.strftime(use_format_str)

    def t_string_to_format_string(self, source_datetime_str, format_str=''):
        """
        t时间字符串转 想要的时间字符串
        :param source_datetime_str:
        :param format_str:
        :return:
        """
        use_format_str = format_str if len(format_str) > 0 else self.default_datetime_format_string
        t_to_datetime = self.t_string_to_datetime(source_datetime_str)
        return t_to_datetime.strftime(use_format_str)

    def object_t_string_to_format_string(self, wait_convert_key_list, format_str='', *args, **kwargs):
        """
        等待转换的对象key
        :param wait_convert_key_list:
        :param format_str:
        :param args:
        :param kwargs:
        :return:
        """
        if args:
            for item in args:
                for wait_convert_key in wait_convert_key_list:
                    wait_convert_str = item.get(wait_convert_key, None)
                    if wait_convert_str:
                        item[wait_convert_key] = self.t_string_to_format_string(wait_convert_str, format_str)
                    else:
                        print('datetime_handle 83: Error convert str', wait_convert_str, wait_convert_key)
            return args
        if kwargs:
            for wait_convert_key in wait_convert_key_list:
                wait_convert_str = kwargs.get(wait_convert_key, None)
                if wait_convert_str:
                    kwargs[wait_convert_key] = self.t_string_to_format_string(wait_convert_str, format_str)
                else:
                    print('datetime_handle 91: Error convert str', wait_convert_str, wait_convert_key)
            return kwargs

    def dict_t_string_to_format_string_after_none(self, wait_convert_keys_list, format_str='', **kwargs):
        """
        等待转换的对象key 大于当前时间返回空字符串
        :param wait_convert_keys_list:
        :param format_str:
        :param kwargs:
        :return:
        """
        use_format_str = format_str if len(format_str) > 0 else self.default_datetime_format_string
        now_datetime = datetime.datetime.now()
        convert_dict = kwargs
        if convert_dict:
            for wait_convert_key in wait_convert_keys_list:
                wait_convert_str = convert_dict.get(wait_convert_key, None)
                if wait_convert_str:
                    current_datetime = self.t_string_to_datetime(wait_convert_str)
                    if not current_datetime or current_datetime > now_datetime:
                        current_datetime_str = ''
                    else:
                        current_datetime_str = self.datetime_format_string(current_datetime, use_format_str)
                    convert_dict[wait_convert_key] = current_datetime_str
            return convert_dict
        return {}

    def list_t_string_to_format_string_after_none(self, wait_convert_keys_list, format_str='', *args):
        """
        等待转换的list 大于当前时间返回空字符串
        :param wait_convert_keys_list:
        :param format_str:
        :param args:
        :return:
        """
        use_format_str = format_str if len(format_str) > 0 else self.default_datetime_format_string
        ret_list = []

        if args:
            for item in args:
                if item:
                    converted_dict = self.dict_t_string_to_format_string_after_none(wait_convert_keys_list,
                                                                                    use_format_str, **item)
                    if converted_dict:
                        ret_list.append(converted_dict)
        return ret_list


class ConvertDatetimestamp(object):
    """
    datetime and timestamp 互转
    from zwutils_methods import ConvertDatetimestamp      # datetime and timestamp 互转
    #    self.cls_convert_date_timestamp = ConvertDatetimestamp()      # datetime and timestamp 互转
    """

    def datetime_convert_timestamp(self, source_datetime: datetime.datetime):
        """
        datetime 转 timestamp
        :param source_datetime:
        :return:
        """
        return int(source_datetime.timestamp())

    def timestamp_convert_datetime(self, source_timestamp: int) -> datetime.datetime:
        """
        timestamp 转 datetime
        :param source_timestamp:
        :return:
        """
        return datetime.datetime.fromtimestamp(source_timestamp)
    

class ConvertBeijingStrTimestamp(object):
    """
    北京时间string and timestamp 互转
    from zwutils_methods import ConvertBeijingStrTimestamp      # 北京时间string and timestamp 互转
    #    self.cls_convert_bj_timestamp =  ConvertBeijingStrTimestamp()    # 北京时间string and timestamp 互转
    """

    def to_timestamp(self, date_str: str, date_format:str="%Y-%m-%d %H:%M:%S"):
        """
        北京时间str 转 timestamp
        :param date_str:
        :return: int
        """
        try:
            # 解析字符串为datetime对象
            datetime_obj = datetime.datetime.strptime(date_str, date_format)
            cst_timezone = pytz.timezone('Asia/Shanghai')
            datetime_with_tz = cst_timezone.localize(datetime_obj)
            # 获取时间戳
            timestamp = datetime_with_tz.timestamp()
            # print("Timestamp:", timestamp)
            return int(timestamp)
        except Exception as e:
            # print(f'......to_timestamp failed(date_str: {date_str}):', e)
            return 0
    
    def to_beijing_str(self, timestamp, date_format:str="%Y-%m-%d %H:%M:%S"):
        """
        timestamp 转北京时间str
            :param timestamp:
            :return: str
        """
        try:
            # 将时间戳转换为 UTC 的datetime对象
            utc_datetime = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)  # 不再使用 utcfromtimestamp，改用 fromtimestamp
            cst_timezone = pytz.timezone('Asia/Shanghai')
            cst_datetime = utc_datetime.astimezone(cst_timezone)
            bj_date_str = cst_datetime.strftime(date_format)
            # print("CST Datetime:", bj_date_str)
            return bj_date_str
        except Exception as e:
            print(e)
            return ''


class DataTimeAdd(object):
    # datetime时间加减

    def datetime_add_seconds(self, source_datetime: datetime.datetime, seconds: int) -> datetime.datetime:
        """
        datetime 加 seconds
        :param source_datetime:
        :param seconds:
        :return:
        """
        return source_datetime + datetime.timedelta(seconds=seconds)

    def datetime_add_minutes(self, source_datetime: datetime.datetime, minutes: int) -> datetime.datetime:
        """
        datetime 加 minute
        :param source_datetime:
        :param minute:
        :return:
        """
        return source_datetime + datetime.timedelta(minutes=minutes)

    def datetime_add_days(self, source_datetime: datetime.datetime, days: int) -> datetime.datetime:
        """
        datetime 加 days
        :param source_datetime:
        :param days:
        :return:
        """
        return source_datetime + datetime.timedelta(days=days)

    def datetime_add_months(self, source_datetime: datetime.datetime, months: int) -> datetime.datetime:
        """
        datetime 加 months
        :param source_datetime:
        :param months:
        :return:
        """
        days_num = months * 30 + int(months / 2)    # 平均每月30天 一年加5天
        return source_datetime + datetime.timedelta(days=days_num)

    def datetime_add_years(self, source_datetime: datetime.datetime, years: int) -> datetime.datetime:
        """
        datetime 加 years
        :param source_datetime:
        :param years:
        :return:
        """
        return source_datetime + datetime.timedelta(years=years)


class TimestampFormat(object):
    """
    时间戳格式化
    """

    def timestamp_format(self, source_timestamp: int, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
        """
        时间戳格式化
        :param source_timestamp:
        :param format_str:
        :return:
        """
        return datetime.datetime.fromtimestamp(source_timestamp).strftime(format_str)
    

if __name__ == '__main__':
    # run: python zwutils_methods/date_handle.py
    cls_convert_bj_timestamp =  ConvertBeijingStrTimestamp()    # 北京时间string and timestamp 互转

    test_date_str = "2023-10-25 14:30:00"
    
    result_timestamp = cls_convert_bj_timestamp.to_timestamp(test_date_str)
    result_bj_data = cls_convert_bj_timestamp.to_beijing_str(result_timestamp)
    print(f'timestamp: {result_timestamp}, 北京时间: {result_bj_data}')

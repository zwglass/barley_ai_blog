import piexif
from PIL import Image     # pip install Pillow, piexif
import copy
import datetime
import random
import pytz
from io import BytesIO


class ImgExifHandle(object):
    """
    from zwutils import ImgExifHandle        # 图片的 exif 修改
    #    self.cls_imgexit = ImgExifHandle()        # 图片的 exif 修改
    """
    def __init__(self):
        pass

    def generate_random_past_date(self):
        """生成 1-7 天前的随机日期时间字符串"""

        days_ago = random.randint(1, 7)
        today = datetime.datetime.now()  # 使用 datetime 获取当前日期和时间
        past_datetime = today - datetime.timedelta(days=days_ago)

        # 格式化日期时间为 EXIF 要求的字符串格式 "YYYY:MM:DD HH:MM:SS"
        past_datetime_str = past_datetime.strftime("%Y:%m:%d %H:%M:%S")
        return past_datetime_str

    def modify_exif_datetime(self, image_path, output_path=None, camera_company_model=None):
        """
        修改图片 EXIF 信息的 DateTime 标签
        camera_company_model = {'make': b"Canon Inc.", 'model': b"Canon EOS R6",  # 佳能制造商}
                               {'make': b"Sony Corporation.", 'model': b"Sony Alpha 7R V",  # 索尼制造商}
                               {'make': b"Apple", 'model': b"iPhone 15 Pro",  # iphone}

        """

        try:
            image = Image.open(image_path)
        except FileNotFoundError:
            print(f"错误：文件 '{image_path}' 未找到。")
            return

        try:
            if camera_company_model is None:
                camera_company_model = {
                    'make': b"Canon Inc.",  # 佳能制造商
                    'model': b"Canon EOS R6",  # 佳能型号 (根据需要修改)
                }
            exif_dict = piexif.load(image.info["exif"]) if "exif" in image.info else {"0th": {}, "Exif": {}, "1st": {}}

            random_datetime_str = self.generate_random_past_date()

            # 0th IFD (主图像信息)
            exif_dict["0th"][piexif.ImageIFD.Make] = camera_company_model['make']  # 制造商
            exif_dict["0th"][piexif.ImageIFD.Model] = camera_company_model['model']  # 型号
            exif_dict["0th"][piexif.ImageIFD.DateTime] = random_datetime_str.encode('utf-8')  # 日期时间
            # exif_dict["0th"][piexif.ImageIFD.Software] = b"Fake Software" # 软件
            # exif_dict["0th"][piexif.ImageIFD.Artist] = b"Fake Artist" # 作者

            # Exif IFD (Exif 信息)
            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = random_datetime_str.encode('utf-8')  # 原始日期时间
            exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = random_datetime_str.encode('utf-8')  # 数字日期时间
            exif_dict["Exif"][piexif.ExifIFD.ExposureTime] = (1, 100)  # 曝光时间 (1/100 秒)
            exif_dict["Exif"][piexif.ExifIFD.FNumber] = (2, 1)  # 光圈值 (f/2)
            exif_dict["Exif"][piexif.ExifIFD.ISOSpeedRatings] = 100  # ISO 感光度
            exif_dict["Exif"][piexif.ExifIFD.ExposureBiasValue] = (0, 1) # 曝光补偿
            exif_dict["Exif"][piexif.ExifIFD.Flash] = 0 # 闪光灯
            exif_dict["Exif"][piexif.ExifIFD.FocalLength] = (50, 1) # 焦距 (50mm)
            exif_dict["Exif"][piexif.ExifIFD.WhiteBalance] = 0 # 白平衡

            # GPS IFD (GPS 信息 - 可选)
            # 如果需要添加 GPS 信息，可以参考 piexif 的文档
            # 例如：
            # exif_dict["GPS"] = {
            #     piexif.GPSIFD.GPSLatitude: (37, 1234, 5678),  # 纬度
            #     piexif.GPSIFD.GPSLongitude: (120, 9876, 5432), # 经度
            #     ...
            # }

            exif_bytes = piexif.dump(exif_dict)
            if output_path is None:
                output_path = copy.deepcopy(image_path)
            image.save(output_path, exif=exif_bytes)
            print(f"成功将 EXIF DateTime 修改为 '{random_datetime_str}' 并保存到 '{output_path}'。")

        except Exception as e:
            print(f"修改 EXIF 信息时发生错误：{e}")

    def read_exif_info(self, image_path):
        # 读取图片 Exif IFD 信息
        try:
            image = Image.open(image_path, mode='r')
            exif_dict = piexif.load(image.info["exif"])   # exif_dict keys: dict_keys(['0th', 'Exif', 'GPS', 'Interop', '1st', 'thumbnail'])

            # 读取 0th IFD 信息
            zeroth_ifd = exif_dict["0th"]
            make = zeroth_ifd.get(piexif.ImageIFD.Make, b"").decode('utf-8')  # 使用 get() 方法，避免 KeyError
            model = zeroth_ifd.get(piexif.ImageIFD.Model, b"").decode('utf-8')
            datetime = zeroth_ifd.get(piexif.ImageIFD.DateTime, b"").decode('utf-8')

            # 读取 Exif IFD 信息
            exif_ifd = exif_dict["Exif"]
            exposure_time = exif_ifd.get(piexif.ExifIFD.ExposureTime, (0, 1))  # 默认值 (0, 1)
            aperture = exif_ifd.get(piexif.ExifIFD.FNumber, (0, 1))  # 默认值 (0, 1)
            iso = exif_ifd.get(piexif.ExifIFD.ISOSpeedRatings, 0)  # 默认值 0

            # 解码字典中的 JSON 字符串
            decoded_dict = {key: value.decode('utf-8') if isinstance(value, str) else value for key, value in exif_dict.items()}
            # print("exif_dict IFD:", decoded_dict, '\n')
            # print("exif_dict IFD keys:", decoded_dict.keys(), '\n')
            gps = decoded_dict['GPS']
            gps_decode = {k: v.decode('utf-8') if isinstance(v, str) else v for k, v in gps.items()}
            print("exif_dict IFD GPS:", gps_decode, '\n')

            # print("0th IFD:", zeroth_ifd)
            # print(f"  Make: {make}")
            # print(f"  Model: {model}")
            # print(f"  DateTime: {datetime}")

            # print("\nExif IFD:", exif_ifd)
            # print(f"  ExposureTime: {exposure_time}")
            # print(f"  Aperture: {aperture}")
            # print(f"  ISO: {iso}")
            return exif_dict
        except FileNotFoundError:
            print(f"错误：文件 '{image_path}' 未找到。")
            return None
        except KeyError:
            print(f"错误：图片 '{image_path}' 不包含 EXIF 信息。")
            return None
        except Exception as e:
            print(f"读取 EXIF 信息时发生错误：{e}")
            return None
        
    def read_xmp_info(self, image_path):
        """
        读取指定图片的 XMP 信息。

        参数:
            图片路径: 图片文件的路径。

        返回:
            包含 XMP 数据的字典。如果发生错误，则返回 None。
        """
        try:
            img = Image.open(image_path)
            xmp_data = img.info.get("XML:XMP")
            if xmp_data:
                # XMP 数据是 XML 格式的字符串，需要解析
                # 可以使用 xml.etree.ElementTree 或其他 XML 解析库
                return xmp_data
            else:
                return None
        except Exception as e:
            print(f"PIL 错误：{e}")
            return None
        
    def generate_realistic_exif_iphone(self, image_path, output_path=None, gps_info=True, latitude=None, longitude=None):
        """
        生成符合实际情况的 EXIF 数据并保存到图片 iphone。
        修改后，0th IFD 中的 DateTime 和 GPS 时间戳将更真实。

        Args:
            image_path: 输入图片路径。
            output_path: 输出图片路径。
        """

        try:
            image = Image.open(image_path)
        except FileNotFoundError:
            print(f"错误：文件 '{image_path}' 未找到。")
            return

        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": b""}

        # 0th IFD
        exif_dict["0th"][piexif.ImageIFD.Make] = b"Apple"
        exif_dict["0th"][piexif.ImageIFD.Model] = b"iPhone 15 Pro"
        exif_dict["0th"][piexif.ImageIFD.Software] = b"iOS 18.2"

        # 生成一个随机的拍摄时间（在过去一年内）
        now = datetime.datetime.now(tz=pytz.utc)  # 使用 UTC 时间
        random_seconds = random.randint(0, 10 * 24 * 3600)  # 过去10天的秒数
        capture_time = now - datetime.timedelta(seconds=random_seconds)

        # 设置 0th IFD 中的 DateTime
        exif_dict["0th"][piexif.ImageIFD.DateTime] = capture_time.strftime("%Y:%m:%d %H:%M:%S").encode('utf-8')
        exif_dict["0th"][piexif.ImageIFD.ImageWidth] = image.width
        exif_dict["0th"][piexif.ImageIFD.ImageLength] = image.height
        exif_dict["0th"][piexif.ImageIFD.Orientation] = 1

        # Exif IFD (与 0th IFD 时间保持一致)
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = exif_dict["0th"][piexif.ImageIFD.DateTime]
        exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = exif_dict["0th"][piexif.ImageIFD.DateTime]
        exif_dict["Exif"][piexif.ExifIFD.ExposureTime] = (1, random.randint(50, 8000))
        exif_dict["Exif"][piexif.ExifIFD.FNumber] = (random.randint(16, 28), 10)
        exif_dict["Exif"][piexif.ExifIFD.ISOSpeedRatings] = random.choice([100, 200, 400, 800])
        exif_dict["Exif"][piexif.ExifIFD.ExposureBiasValue] = (random.randint(-2, 2), 3)
        exif_dict["Exif"][piexif.ExifIFD.Flash] = 0
        exif_dict["Exif"][piexif.ExifIFD.FocalLength] = (random.randint(400, 700), 100)
        exif_dict["Exif"][piexif.ExifIFD.WhiteBalance] = 0
        exif_dict["Exif"][piexif.ExifIFD.PixelXDimension] = image.width
        exif_dict["Exif"][piexif.ExifIFD.PixelYDimension] = image.height
        exif_dict["Exif"][piexif.ExifIFD.LensMake] = b"Apple"
        exif_dict["Exif"][piexif.ExifIFD.LensModel] = b"iPhone 15 Pro back triple camera"

        # GPS IFD (模拟，与拍摄时间关联)
        if gps_info:
            # 台州市的经纬度范围（大致）
            min_latitude = 28.0
            max_latitude = 29.5
            min_longitude = 120.5
            max_longitude = 122.0

            # 生成台州市境内的随机经纬度
            latitude = random.uniform(min_latitude, max_latitude) if latitude is None else latitude
            longitude = random.uniform(min_longitude, max_longitude) if longitude is None else longitude

            exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = b"N" if latitude >= 0 else b"S"
            exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = self._degrees_to_rational(latitude)  # 使用辅助函数转换格式
            exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = b"E" if longitude >= 0 else b"W"
            exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = self._degrees_to_rational(longitude)  # 使用辅助函数转换格式
            # exif_dict["GPS"][piexif.GPSIFD.GPSAltitudeRef] = 0
            # exif_dict["GPS"][piexif.GPSIFD.GPSAltitude] = (random.randint(0, 1000), 1)

            # 设置 GPS 时间戳，与拍摄时间关联，但允许几秒钟的随机偏差
            gps_time = capture_time + datetime.timedelta(seconds=random.randint(-5, 5))  # 随机偏差 -5 到 5 秒
            exif_dict["GPS"][piexif.GPSIFD.GPSTimeStamp] = (gps_time.hour * 3600 + gps_time.minute * 60 + gps_time.second, 1)

        # 1st IFD (缩略图)
        exif_dict["1st"][piexif.ImageIFD.ImageWidth] = image.width // 4
        exif_dict["1st"][piexif.ImageIFD.ImageLength] = image.height // 4
        exif_dict["1st"][piexif.ImageIFD.Compression] = 6
        exif_dict["1st"][piexif.ImageIFD.JPEGInterchangeFormat] = 208
        exif_dict["1st"][piexif.ImageIFD.JPEGInterchangeFormatLength] = len(image.tobytes()) // 100

        # 缩略图数据
        thumbnail = image.resize((32, 32))
        if thumbnail.mode in ('RGBA', 'LA'):
            # 处理透明通道
            # print('thumbnail.mode:', thumbnail.mode, image_path)
            background = Image.new('RGB', thumbnail.size, (255, 255, 255))
            background.paste(thumbnail, mask=thumbnail.split()[-1])
            thumbnail = background.convert('RGB')
        # 获取原始图像的格式
        # original_format = image.format.lower()  # 确保格式名称是小写的
        # 将缩略图保存到内存中的 JPEG 字节流
        thumbnail_io = BytesIO()
        thumbnail.save(thumbnail_io, format='JPEG')  # 明确指定保存为 JPEG 格式
        # thumbnail.save(thumbnail_io, format=original_format)  # 明确指定保存
        thumbnail_bytes = thumbnail_io.getvalue()
        
        # thumbnail_bytes = piexif.dump(piexif.load(thumbnail.info.get("exif", b"")))
        exif_dict["thumbnail"] = thumbnail_bytes

        exif_bytes = piexif.dump(exif_dict)
        output_path = copy.deepcopy(image_path)
        image.save(output_path, exif=exif_bytes)
        # print(f"EXIF 信息已生成并保存到 '{output_path}'。")

    def remove_exif(self, image_path, output_path=None):
        """
        删除图片的 EXIF 信息。

        Args:
            image_path: 输入图片路径。
            output_path: 输出图片路径。
        """
        try:
            # print('remove_exif image_path:', image_path)
            img = Image.open(image_path)
            output_path = copy.deepcopy(image_path) if output_path is None else output_path
            img.save(output_path, exif=b"")  # 将 EXIF 信息设置为空字节
            # print(f"EXIF 信息已从 '{image_path}' 中删除，并保存到 '{output_path}'。")
            return True
        except FileNotFoundError:
            print(f"错误：文件 '{image_path}' 未找到。")
            return False
        except Exception as e:
            print(f"发生错误：{e}")
            return False

    # 辅助函数：将十进制度数转换为度分秒格式
    def _degrees_to_rational(self, degrees):
        degrees_int = int(degrees)
        minutes = (degrees - degrees_int) * 60
        minutes_int = int(minutes)
        seconds = (minutes - minutes_int) * 60
        return (degrees_int, 1), (minutes_int, 1), (int(seconds * 1000), 1000)


if __name__ == '__main__':
    # run: python zwutils_methods\img_exif_handle.py
    cls_imgexit = ImgExifHandle()        # 图片的 exif 修改
    img_path = r'C:\Users\zwgla\Downloads\bg_1.jpg'
    # img_path = r'C:\Users\zwgla\dev\imgs\test_photoshop_1.png'
    # img_path = r'C:\Users\zwgla\Downloads\psimg_4.jpg'
    # cls_imgexit.read_exif_info(img_path)
    xmp_data = cls_imgexit.read_xmp_info(img_path)
    print(xmp_data)
    # cls_imgexit.remove_exif(image_path=img_path)
    # cls_imgexit.generate_realistic_exif_iphone(img_path)

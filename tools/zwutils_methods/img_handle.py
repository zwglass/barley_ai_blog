import sys
import cv2      # pip install opencv-python
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import subprocess
import random
import re
import copy
from vtracer import convert_image_to_svg_py         # pip install vtracer
# 图片基本操作


class ImgHandle(object):
    """
    from zwutils_methods import ImgHandle    # 图片基本操作
    # self.cls_imghandle = ImgHandle()    # 图片基本操作
    """
    def __init__(self):
        pass

    def create_image(self, width, height, color) -> np.ndarray:
        """
        创建一个指定宽高和颜色的 ndarray 图片数据，支持 BGR 或 BGRA 颜色

        参数:
        width (int): 图片的宽度
        height (int): 图片的高度
        color (tuple): 图片的颜色，格式为 (B, G, R) 或 (B, G, R, A)，其中 R, G, B, A 是 0-255 之间的整数

        返回:
        numpy.ndarray: 生成的图片数据，形状为 (height, width, 3) 或 (height, width, 4)
        """
        # 判断颜色是否包含 Alpha 通道
        if len(color) == 4:
            # RGBA 模式，4 通道
            image = np.zeros((height, width, 4), dtype=np.uint8)
        else:
            # RGB 模式，3 通道
            image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 填充颜色
        image[:, :] = color
        return image
    
    def img_to_svg(self, source_img_path, output_path) -> bool:
        # 图片转 svg
        convert_image_to_svg_py(source_img_path, output_path)
        return True

    def img_to_ndarray(self, img_path) -> np.ndarray:
        """
        将指定路径的图片读取为 NumPy 数组。

        参数:
            img_path: 图片文件的路径。
            颜色模式: cv2.IMREAD_COLOR (默认) 表示读取彩色图像。
                    cv2.IMREAD_GRAYSCALE 表示读取灰度图像。
                    其他模式请参考 OpenCV 文档。

        返回:
            NumPy 数组。如果读取失败，则返回 None。
        """
        try:
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                return img
            else:
                print(f"无法读取图片：{img_path}")
                return None
        except Exception as e:
            print(f"img_to_ndarray 发生错误：{e}", img_path)
            return None
        
    def ndarray_to_img(self, img:np.ndarray, write_path):
        """
        使用 OpenCV 库将 NumPy 数组保存为图片。

        参数:
            numpy_数组: 要保存的 NumPy 数组。
            图片路径: 图片文件的路径。
        """
        try:
            result = cv2.imwrite(write_path, img)  # 保存图像
            # print(f"图片已保存到：{write_path}")
            return result
        except Exception as e:
            print(f"ndarray_to_img 发生错误：{e}")
            return False

    def width_height(self, img:np.ndarray) -> tuple:
        # 图片宽和高
        # h, w, channels = img.shape
        h, w = img.shape[:2]
        return w, h
    
    def text_width_height(self, text, bg_ndarray, font_path, font_size=16):
        # Compute the size of a text in a PIL font
        # 创建空白图像
        w, h =self.width_height(bg_ndarray)
        font = ImageFont.truetype(font_path, font_size)
        img = Image.new("RGB", (w, h), (255, 255, 255))

        # 创建绘图对象
        draw = ImageDraw.Draw(img)
        # 获取文本的边界框
        bbox = draw.textbbox((0, 0), text, font=font)

        # bbox 返回的是 (left, upper, right, lower)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        return text_width, text_height
    
    def check_alpha(self, img_path) -> bool:
        # 判断图片是否有 alpha 通道; 至少有 50 个像素 alpha == 0
        img_ndarr = self.img_to_ndarray(img_path=img_path)
        have_alpha = img_ndarr.shape[2] == 4
        if not have_alpha:
            return False
        # 分离Alpha通道
        alpha_channel = img_ndarr[:, :, 3]
        # 统计Alpha值为0的像素数量
        transparent_pixels = np.sum(alpha_channel == 0)
        return transparent_pixels > 30      # 透明像素数量 > 30 才是有透明图层
    
    def add_alpha(self, img:np.ndarray) -> np.ndarray:
        """
        检查 NumPy 数组是否具有 alpha 通道，如果没有，则添加一个 alpha 通道并设置为透明。

        参数:
            ndarray: 要检查的 NumPy 数组。

        返回:
            如果 ndarray 具有 alpha 通道，则返回原始 ndarray。
            如果 ndarray 没有 alpha 通道，则返回添加了 alpha 通道的 ndarray。
        """

        if img.shape[2] == 4:  # Already has an alpha channel
            return img

        else:  # Add alpha channel
            height, width = img.shape[:2]

            # Correct way to create the alpha channel with the right dtype:
            alpha_channel = np.full((height, width, 1), 255, dtype=img.dtype)

            # Reshape img to have a shape of (height, width, 3) if it's grayscale
            if img.ndim == 2:
                img = img.reshape(height, width, 1) # Reshape to (height, width, 1)

            # Concatenate along the last axis (axis=2). Both should have 3 dimensions now.
            alpha_ndarray = np.concatenate((img, alpha_channel), axis=2)
            return alpha_ndarray
        
    def del_alpha(self, img:np.ndarray) -> np.ndarray:
        """
        从 NumPy 数组中删除 alpha 通道。

        参数:
            ndarray: 要删除 alpha 通道的 NumPy 数组。

        返回:
            如果 ndarray 具有 alpha 通道，则返回删除 alpha 通道后的 ndarray。
            如果 ndarray 没有 alpha 通道，则返回原始 ndarray。
        """

        if img.shape[2] == 4:  # 检查是否具有 4 个通道（RGBA）
            return img[:, :, :3]  # 删除最后一个通道（alpha 通道）
        else:
            return img  # 如果没有 alpha 通道，则直接返回
        
    def resize_ndarray(self, target_size, img:np.ndarray) -> np.ndarray:
        # 缩放图片 np.ndarray
        target_width, target_height = target_size
        if sys.platform == 'darwin':  # mac系统使用 sips 缩放图片   temp_files
            temp_files_dir = Path(__file__).resolve().parent.parent / 'temp_files'
            tempimg_path =  str(temp_files_dir / 'temp_xxxxxxx_mac.png')
            tempimg_out_path = str(temp_files_dir / 'temp_xxxxxxx_mac_out.png')
            # print('Current temp_files_dir:', temp_files_dir)
            self.ndarray_to_img(img, write_path=tempimg_path)
            self.mac_resize_image(input_path=tempimg_path, output_path=tempimg_out_path, width=target_width, height=target_height)
            resized_ndarray = self.img_to_ndarray(tempimg_out_path)
            # 删除临时文件
            # os.remove(tempimg_path)
            # os.remove(tempimg_out_path)
            return resized_ndarray
        else:  # 非mac系统
            # Resize the image to the new dimensions 缩放图片，并使用最近邻插值（default）INTER_NEAREST
            # interpolation: INTER_LINEAR 线性插值,INTER_CUBIC 三次样条插值,INTER_AREA 区域插值,INTER_NEAREST 最近邻插值
            resized_img = cv2.resize(cropped_img, dsize=(target_width, target_height), interpolation=cv2.INTER_NEAREST)
            return resized_img

    def resize_ndarray_by_width(self, target_width, img:np.ndarray) -> np.ndarray:
        # 修改图片尺寸, 改变宽度, 比例不变

        # Get the original height and width of the image
        original_height, original_width, _ = img.shape

        # Calculate the new height based on maintaining aspect ratio with a width of 750 pixels
        aspect_ratio = original_height / original_width
        new_height = int(aspect_ratio * float(target_width))

        # Resize the image to the new dimensions
        # resized_img = cv2.resize(img, (target_width, new_height))
        resized_img = self.resize_ndarray(target_size=(target_width, new_height), img=img)

        return resized_img
    
    def resize_ndarray_by_height(self, target_height, img:np.ndarray) -> np.ndarray:
        # 修改图片尺寸, 改变高度, 比例不变

        # Get the original height and width of the image
        # original_height, original_width, _ = img.shape
        original_height, original_width = img.shape[:2]  # Get height and width

        # Calculate the new height based on maintaining aspect ratio with a width of 750 pixels
        aspect_ratio = original_width / original_height
        new_width = int(round(aspect_ratio * target_height)) # Round to the nearest integer

        # Resize the image to the new dimensions # Resize the image. dsize MUST be a tuple of integers.
        # resized_img = cv2.resize(img, (new_width, int(target_height)))
        resized_img = self.resize_ndarray(target_size=(new_width, int(target_height)), img=img)

        return resized_img
    
    def resize_ndarray_within_bounds(self, target_width, target_height, img:np.ndarray, mode='fit'):
        """
        缩放图片到目标宽高范围内，保持原始宽高比
        
        参数:
            image: numpy.ndarray, 输入图片(HWC格式)
            target_width: int, 目标宽度
            target_height: int, 目标高度
            mode: str, 缩放模式 ('fit' 或 'fill')
        返回:
            numpy.ndarray: 缩放后的图片
        """
        if not isinstance(img, np.ndarray):
            raise ValueError("输入必须是numpy数组")
        
        if len(img.shape) not in (2, 3):
            raise ValueError("输入必须是2D(灰度)或3D(彩色)图片")
        
        # 获取原始高度和宽度
        original_height, original_width = img.shape[:2]
        
        # 计算宽高比
        width_ratio = target_width / original_width
        height_ratio = target_height / original_height
        
        # 选择较小的缩放比例，确保图片不超出目标尺寸
        scale = min(width_ratio, height_ratio)
        if mode == 'fill':
            # 占满目标尺寸, 多出部分居中裁剪
            scale = max(width_ratio, height_ratio)
        
        # 计算新尺寸
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        # 缩放图片 np.ndarray
        resized_img = self.resize_ndarray(target_size=(new_width, new_height), img=img)

        if mode == 'fill':
            # 占满目标尺寸, 多出部分居中裁剪
            resized_img = self.crop_ndarray(target_width, target_height, resized_img)
        
        return resized_img
    
    def crop_ndarray(self, target_width:int, target_height:int, img:np.ndarray, start_position=None) -> np.ndarray:
        # ndarray 数据的图片裁剪; start_position == None 居中裁剪
        source_width, source_height = self.width_height(img)
        # 计算新尺寸
        crop_width = copy.deepcopy(target_width) if target_width < source_width else source_width
        crop_height = copy.deepcopy(target_height) if target_height < source_height else source_height

        if start_position is None:
            top_offset = (source_height - crop_height) // 2
            left_offset = (source_width - crop_width) // 2
        else:
            left_offset, top_offset = start_position

        cropped_image = img[top_offset:top_offset + crop_height, left_offset:left_offset + crop_width]
        return cropped_image

    def text_to_image(self, text, font_path, font_size, text_color=(0,0,0),
                  padding=2, spacing=4, stroke_width=0):
        """
        将文字转换为透明背景的 PIL 图像，并返回转换后的 cv2 图像（通过 self.pil_to_cv2）。
        padding: 周围空白像素，避免抗锯齿被裁掉
        spacing: 多行间距
        stroke_width: 如需描边，设置描边宽度
        """
        font = ImageFont.truetype(font_path, font_size)

        # 用临时 draw 计算精确边界框（支持多行）
        tmp = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        tmp_draw = ImageDraw.Draw(tmp)
        left, top, right, bottom = tmp_draw.textbbox(
            (0, 0), text, font=font, spacing=spacing, stroke_width=stroke_width
        )

        width = (right - left) + padding * 2
        height = (bottom - top) + padding * 2

        # 创建目标图像并把绘制原点平移 -left, -top，再加 padding
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text(
            (-left + padding, -top + padding),
            text,
            font=font,
            fill=(*text_color, 255),
            spacing=spacing,
            stroke_width=stroke_width
        )

        return self.pil_to_cv2(image)

    def ndarray_write_text(self, cv2_ndarray, text, pos, font_path, font_size=16, color=None, font_path_en=None):
        """
        cv2 ndarray 写入文字
        """
        pil_img = self.cv2_to_pil(cv2_ndarray)
        # 创建一个 ImageDraw 对象来绘制
        draw = ImageDraw.Draw(pil_img)

        if font_path_en is not None:
            # 中英文混排
            # 正则匹配非中文（英文、数字、符号等）和中文
            start_pos = copy.deepcopy(pos)
            pattern = re.compile(r"([^\u4e00-\u9fff]+|[\u4e00-\u9fff]+)")
            segments = pattern.findall(text)
            x = start_pos[0]
            for segment in segments:
                if re.search(r"[\u4e00-\u9fff]", segment):  # 如果是中文
                    font = ImageFont.truetype(font_path, font_size)
                else:  # 如果是英文/符号
                    font = ImageFont.truetype(font_path_en, font_size)
                
                # 绘制当前片段
                draw.text((x, start_pos[1]), segment, font=font, fill=self.convert_color(color))
                # 更新 x 位置（避免重叠）
                x += font.getlength(segment)
        else:
            font = ImageFont.truetype(font_path, font_size)
            if color is None:
                color = (10, 10, 10)

            draw.text(pos, text, font=font, fill=self.convert_color(color))
        image = self.pil_to_cv2(pil_img)
        return image
    
    def put_text_multiline(self, image, text, position, font_path, font_size, color,
                     line_spacing=1.5, max_width=None, paragraph_spacing=1.2):
        """
        支持换行符的文字绘制函数
        
        参数:
            image: 输入图像
            text: 可包含换行符的文本
            position: 起始位置
            paragraph_spacing: 段落间距倍数
            其他参数同基础函数
            
        返回:
            tuple: (修改后的图像, 总宽度, 总高度)
        """
        x, y = position
        paragraphs = text.split('\n')
        total_height = 0
        max_width_actual = 0
        
        current_img = image.copy()
        
        for para in paragraphs:
            if not para:  # 空行处理
                _, _, h = self.put_text_word_wrap(
                    current_img, " ", (x, y), font_path, font_size, color,
                    line_spacing, max_width
                )
                total_height += h * paragraph_spacing
                y += int(h * paragraph_spacing)
                continue
                
            img_with_text, w, h = self.put_text_word_wrap(
                current_img, para, (x, y), font_path, font_size, color,
                line_spacing, max_width
            )
            
            max_width_actual = max(max_width_actual, w)
            total_height += h * (paragraph_spacing if para != paragraphs[-1] else 1)
            y += int(h * paragraph_spacing)
            current_img = img_with_text
        
        return current_img, max_width_actual, total_height
    
    def put_text_word_wrap(self, image, text, position, font_path, font_size, color, line_spacing=1.5, max_width=None):
        """
        在图像上绘制中文（支持自动换行）
        
        参数:
            image: 输入图像 (numpy数组, BGR格式)
            text: 要绘制的文字 (支持中文)
            position: 文字起始位置 (x, y)
            font_path: 中文字体文件路径 (如 "simsun.ttc")
            font_size: 字体大小
            color: 文字颜色 (BGR格式)
            thickness: 文字粗细 (仅保留参数，实际使用字体大小控制)
            line_spacing: 行间距倍数 (默认1.5)
            max_width: 最大行宽度 (像素)，如果为None则使用图像宽度减去x坐标
            
        返回:
            tuple: (修改后的图像, 文字区域宽度, 文字区域高度)
        """
        # 将OpenCV图像转换为PIL格式（RGB）
        # pil_cv2_convert_method = cv2.COLOR_BGRA2RGBA if image.shape[2] == 4 else cv2.COLOR_BGR2RGB
        # img_pil = Image.fromarray(cv2.cvtColor(image, pil_cv2_convert_method))
        img_pil = self.cv2_to_pil(image)
        # print('image.shape[2]:', image.shape[2])
        draw = ImageDraw.Draw(img_pil)

        x, y = position
        if max_width is None:
            max_width = image.shape[1] - x
        else:
            max_width = min(max_width, image.shape[1] - x)
        
        # 加载中文字体
        font = ImageFont.truetype(font_path, font_size)
        
        # 分割文本为字符（处理中文）
        chars = list(text)
        lines = []
        current_line = []
        current_line_width = 0
        
        # 计算空格宽度（用于英文）
        space_width = font.getlength(' ')
        
        for char in chars:
            if char == ' ':
                char_width = space_width
            else:
                char_width = font.getlength(char)
            
            # 检查是否超出最大宽度
            if current_line_width + char_width <= max_width:
                current_line.append(char)
                current_line_width += char_width
            else:
                lines.append(''.join(current_line))
                current_line = [char]
                current_line_width = char_width
        
        # 添加最后一行
        if current_line:
            lines.append(''.join(current_line))
        
        # 计算总高度
        line_height = int(font_size * line_spacing)
        total_height = len(lines) * line_height
        
        # 计算总宽度
        total_width = 0
        for line in lines:
            line_width = int(font.getlength(line))
            if line_width > total_width:
                total_width = line_width
        
        # 绘制每一行文本
        y_offset = y
        for line in lines:
            draw.text((x, y_offset), line, font=font, fill=(color[2], color[1], color[0]))  # BGR转RGB
            y_offset += line_height
        
        # 将PIL图像转回OpenCV格式
        # result_img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        result_img = self.pil_to_cv2(img_pil)
        
        return result_img, total_width, total_height
    
    def combine_ndarray(self, a_array, b_array, position=(0, 0)):
        """
        将图片 img_b 放在图片 img_a 的位置
        
        参数:
            img_a: 图片 a, 格式为 cv2.imread(img_a_path) numpy 数组
            img_b: 图片 b, 格式为 cv2.imread(img_b_path) numpy 数组
            position: (x, y)
                x: 放置的左上角坐标中的 x 坐标
                y: 放置的左上角坐标中的 y 坐标
            
        返回:
            结果图片，格式与 img_a 一致(numpy 数组)
        """
        x, y = position[0], position[1]

        # 获取img_a和img_b的尺寸
        a_height, a_width = a_array.shape[:2]
        b_height, b_width = b_array.shape[:2]

        b_x_end = min(b_width, a_width-x)
        b_y_end = min(b_height, a_height-y)
        cropped_b_array = b_array[:b_y_end, :b_x_end, :]

        # 检查位置是否在img_a范围内
        if x < 0 or y < 0 or x > a_width or y > a_height:
            print('position not in image A...')
            return a_array  # 不在范围内，直接返回a_array
        # 初始化 result变量为 a_array 的副本
        result = a_array.copy()
        
        # 判断是否有Alpha通道
        has_alpha_a = len(a_array.shape) == 3 and a_array.shape[2] == 4
        has_alpha_b = len(b_array.shape) == 3 and b_array.shape[2] == 4

        y1 = y + b_y_end
        x1 = x + b_x_end

        if not has_alpha_a:
            # img_a 没有Alpha通道
            if has_alpha_b:
                result = self.replace_pixels(img_a=a_array, img_b=cropped_b_array, start_position=position)
            else:
                # img_b 没有Alpha通道，直接替换
                result[y:y1, x:x1] = cropped_b_array
        else:
            # img_a 带有Alpha通道
            if not has_alpha_b:
                # img_b 没有Alpha通道，将img_b的像素替换到img_a上，并设置alpha为255
                rgba_image = np.zeros((b_y_end, b_x_end, 4), dtype=np.uint8)
                rgba_image[:, :, :3] = cropped_b_array
                rgba_image[:, :, 3] = 255
                result[y:y1, x:x1] = rgba_image
            else:
                result = self.replace_pixels(img_a=a_array, img_b=cropped_b_array, start_position=position)

        return result
    
    def replace_pixels(self, img_a, img_b, start_position):
        # 循环替换 img_a 的像素
        img_a_have_alpha = img_a.shape[2] == 4
        height, width = img_b.shape[:2]
        for i in range(height):
            for j in range(width):
                # 获取当前像素值
                pixel = img_b[i, j]
                if len(pixel) == 4 and pixel[-1] > 50:
                    img_a_replace_piexl_pos = self.compute_img_a_pixel_position(start_position, (j, i))
                    # 计算替换的像素
                    replace_pixel = [*pixel[:3], 255] if img_a_have_alpha else pixel[:3]
                    img_a[img_a_replace_piexl_pos[1], img_a_replace_piexl_pos[0]] = replace_pixel
        return img_a
    
    def compute_img_a_pixel_position(self, start_position, img_b_pixel_position):
        # 计算对应 img_a 的像素坐标
        height_a = start_position[1] + img_b_pixel_position[1]
        width_a = start_position[0] + img_b_pixel_position[0]
        return (width_a, height_a)
    
    def cv2_to_pil(self, cv_img):
        """
        Convert an OpenCV image (BGR or BGRA) to a Pillow image (RGB or RGBA).
        
        Parameters:
        - cv_img: OpenCV image (numpy array)
        
        Returns:
        - pil_img: Pillow image (Image object)
        """
        if cv_img.shape[2] == 4:  # BGRA format, with alpha channel
            pil_img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGRA2RGBA))
        else:  # BGR format, without alpha channel
            pil_img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
        
        return pil_img
    
    def pil_to_cv2(self, pil_img):
        """
        Convert a Pillow image (RGB or RGBA) to an OpenCV image (BGR or BGRA).
        
        Parameters:
        - pil_img: Pillow image (Image object)
        
        Returns:
        - cv_img: OpenCV image (numpy array)
        """
        if pil_img.mode == 'RGBA':  # RGBA format, with alpha channel
            cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGBA2BGRA)
        else:  # RGB format, without alpha channel
            cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        return cv_img
    
    def convert_color(self, color):
        return (color[2], color[1], color[0])
    
    def concatenate_imgs(self, ndarray_a, ndarray_b):
        # 拼接两张图片
        # 获取两张图像的尺寸
        w_a, h_a = self.width_height(ndarray_a)
        w_b, h_b = self.width_height(ndarray_b)

        ndarray_a_with_alpha = self.add_alpha(ndarray_a)
        ndarray_b_with_alpha = self.add_alpha(ndarray_b)

        ret_ndarray_w = max(w_a, w_b)
        ret_ndarray_h = h_a + h_b

        pos_a_x = int(ret_ndarray_w / 2 - w_a / 2)
        pos_b_x = int(ret_ndarray_w / 2 - w_b / 2)
        pos_a = (pos_a_x, 0)
        pos_b = (pos_b_x, h_a)

        # 创建空白图片, 带alpha通道
        ret_ndarray = np.zeros((ret_ndarray_h, ret_ndarray_w, 4), dtype='uint8')
        # 拼接两张图片
        ret_ndarray = self.combine_ndarray(ret_ndarray, ndarray_a_with_alpha, pos_a)
        ret_ndarray = self.combine_ndarray(ret_ndarray, ndarray_b_with_alpha, pos_b)

        return ret_ndarray

    def concatenate_imgs_in_dir(self, dir_path, prefix=None, output_path:str=None) -> np.ndarray | None:
        '''
        将指定目录下的图片拼接成一张大图
        :param dir_path: 图片所在的目录
        :return: ndarray
        '''
        # 获取目录下的所有图片文件
        imgs_paths = self.get_imgs_paths_in_dir(dir_path, prefix=prefix)
        return self.concatenate_imgs_paths(imgs_paths=imgs_paths, output_path=output_path)
    
    def concatenate_imgs_paths(self, imgs_paths:list, output_path:str=None) -> np.ndarray | None:
        '''
        将指定目录下的图片拼接成一张大图
        :param dir_path: 图片所在的目录
        :return: ndarray
        '''
        # 获取目录下的所有图片文件
        if len(imgs_paths) == 0:
            return None
        elif len(imgs_paths) == 1:
            ret_ndarr = self.img_to_ndarray(imgs_paths[0])
            if output_path is not None:
                self.ndarray_to_img(ret_ndarr, output_path)     # 保存图片
            return ret_ndarr

        # 初始化拼接图片的宽高
        con_img_w, con_img_h = 0, 0
        # 获取所有图片的宽高
        for img_path in imgs_paths:
            img = self.img_to_ndarray(img_path)
            img_w, img_h = self.width_height(img)
            con_img_h += img_h
            con_img_w = max(con_img_w, img_w)

        con_img = self.img_to_ndarray(imgs_paths[0])
        for i in range(len(imgs_paths)):
            if i == 0:
                continue
            current_ndarray = self.img_to_ndarray(imgs_paths[i])
            con_img = self.concatenate_imgs(con_img, current_ndarray)
        if  output_path is not None:
            self.ndarray_to_img(con_img, output_path)     # 保存图片
        return con_img
    
    def check_img(self, img_path) -> bool:
        # 验证是否是图片
        try:
            if not Path(img_path).is_file():   # 不是文件直接返回False
                return False
            
            # Load the file into memory (assuming it's in BMP, JPEG, PNG, etc. format)
            img = cv2.imread(img_path)

            if img is None:
                # print("Error: Unable to load the file.")
                return False
            else:
                # If the image was loaded, verify its structure and contents
                if len(img.shape) == 3 or (len(img.shape) == 2 and img.dtype == 'uint8'):
                    # Check for valid image dimensions and data type
                    height, width = img.shape[:2]
                    channels = img.shape[2] if len(img.shape) > 2 else None

                    # print(f"Image loaded successfully: {height}x{width}, {channels} channels")
                    return True
                else:
                    print("Error: The file appears to be an image, but its structure is invalid.")
                    return False
        except Exception as e:
            print('Error:', e)
            return False

    def get_imgs_paths_in_dir(self, folder_path, prefix=None):
        '''
        获取指定目录下的所有图片路径
        :param dir_path: 图片所在的目录
        :param prefix: 图片名称前缀 tuple
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
    
    def resize_and_fit(self, img_path, save_path, target_size) -> str:
        # 修改图片尺寸, 不够部分修改为白底图
        img = self.img_to_ndarray(img_path=img_path)
        original_height, original_width, _ = img.shape
        target_width, target_height = target_size

        # 计算缩放比例, 取比例小的
        ratio_w = target_width / original_width
        ratio_h = target_height / original_height
        resize_raito = min(ratio_w, ratio_h)   # 背景图是比目标尺寸的

        # 计算修改的宽和高
        resize_w = int(original_width * resize_raito)
        resize_h = int(original_height * resize_raito)

        # Resize the image to the new dimensions 缩放图片，并使用最近邻插值（default）INTER_NEAREST
        # interpolation: INTER_LINEAR 线性插值,INTER_CUBIC 三次样条插值,INTER_AREA 区域插值,INTER_NEAREST 最近邻插值
        # resized_img = cv2.resize(img, (resize_w, resize_h), interpolation=cv2.INTER_AREA)
        resized_img = self.resize_ndarray(target_size=(resize_w, resize_h), img=img)

        # 计算裁剪位置
        pos_x = (target_width - resize_w) // 2
        pos_y = (target_height - resize_h) // 2
        bg_color = (255, 255, 255)
        if img.shape[2] == 4:   # 原图有alpha通道使用透明底
            bg_color = (0, 0, 0, 0)
        bg_ndarray = self.create_image(target_width, target_height, bg_color)
        ret_ndarray = self.combine_ndarray(bg_ndarray, resized_img, (pos_x, pos_y))
        cv2.imwrite(save_path, ret_ndarray)
        return save_path
    
    def resize_and_cutout(self, target_width, target_height, img_path, save_path) -> str:
        # 修改图片尺寸, 多余部分裁剪
        # 裁剪为目标的比例
        # test_cut_img_path = '/Users/senmalay/v_programs/dev/self_apps/pump_taobao_handle/temp_files/test_0.png'
        cropped_img = self.crop_img_with_target_ratio(img_path=img_path, target_size=(target_width, target_height))
        # cv2.imwrite(test_cut_img_path, cropped_img)
        # print('cropped_img:', cropped_img)
        if cropped_img is None:
            print(f"Error: Unable to read image at {img_path}")
            return None

        # Resize the image to the new dimensions 缩放图片，并使用最近邻插值（default）INTER_NEAREST
        # interpolation: INTER_LINEAR 线性插值,INTER_CUBIC 三次样条插值,INTER_AREA 区域插值,INTER_NEAREST 最近邻插值
        # resized_img = cv2.resize(cropped_img, dsize=(target_width, target_height), interpolation=cv2.INTER_NEAREST)
        resized_img = self.resize_ndarray(target_size=(target_width, target_height), img=cropped_img)

        # Save the modified image as a JPG file
        cv2.imwrite(save_path, resized_img)
        return save_path
    
    def crop_img_with_target_ratio(self, img_path, target_size:tuple) -> np.ndarray:
        # 按目标比例裁剪图片. target_size: (width, heigth)
        target_width, target_height = target_size
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError(f"Failed to load image from {img_path}")
        # 获取图片尺寸
        original_height, original_width = img.shape[:2]

        # 计算缩放比例, 取比例大的
        target_ratio = target_width / target_height
        original_ratio = original_width / original_height

        if original_ratio > target_ratio:
            # 如果原始图片更宽，高度不变，裁剪宽度
            resize_width = int(original_height * target_ratio)
            left_offset = (original_width - resize_width) // 2
            # print(f'...original_width-{original_width};  resize_width-{resize_width};  left_offset-{left_offset};')
            cropped_image = img[0:original_height, left_offset:left_offset + resize_width]
            return cropped_image
        elif original_height == target_ratio:
            return img
        else:
            # 如果原始图片更高，宽度不变裁剪高度
            resize_height = int(original_width / target_ratio)
            top_offset = (original_height - resize_height) // 2
            cropped_image = img[top_offset:top_offset + resize_height, 0:original_width]
            return cropped_image
        
    def add_round_corner(self, cv2_ndarray, output_path=None, corner_radius=None):
        # 转换为圆角图 (.png)
        image_with_alpha = self.add_alpha(cv2_ndarray)
        # 获取图像的高度和宽度
        height, width = image_with_alpha.shape[:2]

        # 创建一个与图像相同大小的黑色图像
        # mask = np.zeros((height, width), dtype=np.uint8)
        mask = np.ones((height, width), dtype=np.uint8) * 255  # 初始为全白

        if corner_radius is not None:
            # 在四个角画上圆形
            # 左上角
            mask[0:corner_radius, 0:corner_radius] = 0
            cv2.circle(mask, (corner_radius, corner_radius), corner_radius, 255, -1)
            # 右上角
            mask[0:corner_radius, width - corner_radius:width] = 0
            cv2.circle(mask, (width - corner_radius, corner_radius), corner_radius, 255, -1)
            # 左下角
            mask[height-corner_radius:height, 0:corner_radius] = 0
            cv2.circle(mask, (corner_radius, height - corner_radius), corner_radius, 255, -1)
            # 右下角
            mask[height-corner_radius:height, width-corner_radius:width] = 0
            cv2.circle(mask, (width - corner_radius, height - corner_radius), corner_radius, 255, -1)
        else:
            # 创建一个圆角矩形
            center = (width // 2, height // 2)
            axes = (width // 2, height // 2)
            angle = 0
            startAngle = 0
            endAngle = 360
            cv2.ellipse(mask, center, axes, angle, startAngle, endAngle, 255, -1)

        # 使用圆角蒙版与原始图像相乘
        # result = cv2.bitwise_and(cv2_ndarray, cv2_ndarray, mask=mask)
        image_with_alpha[:, :, 3] = mask  # 将mask作为alpha通道

        if output_path is not None:
            cv2.imwrite(output_path, image_with_alpha)
        return image_with_alpha
    
    def resize_white_bg_img(self, img_path, save_path, target_size):
        # 修改白色图和透明背景图尺寸; target_size: (width, heigth);
        img = self.img_to_ndarray(img_path=img_path)
        original_height, original_width, _ = img.shape
        target_width, target_height = target_size

        # 计算缩放比例, 取比例小的
        ratio_w = target_width / original_width
        ratio_h = target_height / original_height
        resize_raito = min(ratio_w, ratio_h) * 0.85   # 背景图是比目标尺寸的 0.85

        # 计算修改的宽和高
        resize_w = int(original_width * resize_raito)
        resize_h = int(original_height * resize_raito)

        # Resize the image to the new dimensions 缩放图片，并使用最近邻插值（default）INTER_NEAREST
        # interpolation: INTER_LINEAR 线性插值,INTER_CUBIC 三次样条插值,INTER_AREA 区域插值,INTER_NEAREST 最近邻插值
        # resized_img = cv2.resize(img, (resize_w, resize_h), interpolation=cv2.INTER_AREA)
        resized_img = self.resize_ndarray(target_size=(resize_w, resize_h), img=img)
        name_idx = Path(img_path).name.split('_')[1]

        if name_idx.startswith('52'):
            bg_ndarray = self.create_image(target_width, target_height, (0, 0, 0, 0))   # d_52 开头的是透明底图
        else:
            bg_ndarray = self.create_image(target_width, target_height, (255, 255, 255))   # d_51 或其它开头的是白底图
        
        pos_x = (target_width - resize_w) // 2
        pos_y = (target_height - resize_h) // 2
        ret_ndarray = self.combine_ndarray(bg_ndarray, resized_img, (pos_x, pos_y))
        cv2.imwrite(save_path, ret_ndarray)
        return save_path
    
    def mac_resize_image(self, input_path, output_path, width=None, height=None):
        """
        使用 macOS 的 sips 工具缩放图片
        :param input_path: 输入图片路径
        :param output_path: 输出图片路径
        :param width: 目标宽度（可选）
        :param height: 目标高度（可选）
        """
        if not width or not height:
            raise ValueError("必须指定宽度和高度")

        # 构建 sips 命令
        # command = ['sips', '--resampleHeightWidth' if height else '--resampleWidth', str(height if height else width), input_path, '--out', output_path]
        # command = ['sips', '-z', str(height), str(width), input_path, '--out', output_path, '>', '/dev/null', ]
        command = ['sips', '-z', str(height), str(width), input_path, '--out', output_path]

        # 执行命令
        subprocess.run(command, stdout=subprocess.DEVNULL, check=True)

        # print(f"图片已缩放并保存到 {output_path}")

    def apply_glass_effect(self, img:np.ndarray, radius=5):
        """
        为图像添加毛玻璃效果
        
        参数:
            img: 输入图像 (BGR格式)
            radius: 毛玻璃效果的半径大小，值越大效果越模糊
            
        返回:
            处理后的带有毛玻璃效果的图像
        """
        # 获取图像尺寸
        h, w = img.shape[:2]
        
        # 创建输出图像
        result = np.zeros_like(img)
        
        # 遍历每个像素
        for y in range(h):
            for x in range(w):
                # 随机选择邻域内的一个像素
                rand_y = random.randint(max(0, y - radius), min(h - 1, y + radius))
                rand_x = random.randint(max(0, x - radius), min(w - 1, x + radius))
                
                # 将随机选择的像素颜色赋给当前像素
                result[y, x] = img[rand_y, rand_x]
        
        return result

    def improved_glass_effect(self, img, radius=5, noise_intensity=20):
        # 先高斯模糊
        blurred = cv2.GaussianBlur(img, (radius*2+1, radius*2+1), 0)
        
        # 添加随机噪声增强颗粒感
        noise = np.random.randint(-noise_intensity, noise_intensity, img.shape, dtype=np.int16)
        result = np.clip(blurred.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        return result

    def blend_images(self, img1, img2):
        """
        将两张带有Alpha通道的图片叠加，返回叠加后的ndarray数据。
        参数：
            img1: numpy数组，底层图像，形状为(H, W, 4)，数据类型可以是uint8或float。
            img2: numpy数组，顶层图像，形状与img1相同。
        返回：
            numpy数组，叠加后的图像，形状和数据类型与输入相同。
        """
        # img1_uint8 = img1.astype(np.uint8)
        # img2_uint8 = img2.astype(np.uint8)
        # blended_uint8 = blend_images(img1_uint8, img2_uint8)

        # 检查形状和通道数
        assert img1.shape == img2.shape, "Images must have the same shape"
        assert img1.shape[2] == 4 and img2.shape[2] == 4, "Images must have 4 channels (RGBA)"
        
        # 保存原始数据类型
        dtype = img1.dtype
        
        # 转换为浮点型并归一化到0-1范围（如果是整数类型）
        if np.issubdtype(dtype, np.integer):
            img1 = img1.astype(np.float32) / 255.0
            img2 = img2.astype(np.float32) / 255.0
        else:
            img1 = img1.astype(np.float32)
            img2 = img2.astype(np.float32)
        
        # 分解通道
        bottom_rgb = img1[..., :3]
        bottom_alpha = img1[..., 3]
        top_rgb = img2[..., :3]
        top_alpha = img2[..., 3]
        
        # 计算合成后的Alpha
        alpha_out = top_alpha + bottom_alpha * (1 - top_alpha)
        
        # 计算分子部分
        numerator = top_rgb * top_alpha[..., np.newaxis] + bottom_rgb * bottom_alpha[..., np.newaxis] * (1 - top_alpha[..., np.newaxis])
        
        # 计算合成后的RGB，处理除以零的情况
        rgb_out = np.zeros_like(numerator)
        valid = alpha_out > 0
        rgb_out[valid] = numerator[valid] / alpha_out[valid][:, np.newaxis]
        
        # 合并通道
        result = np.zeros_like(img1)
        result[..., :3] = rgb_out
        result[..., 3] = alpha_out
        
        # 转换回原始数据类型
        if np.issubdtype(dtype, np.integer):
            result = (result * 255).clip(0, 255).astype(dtype)
        else:
            result = result.astype(dtype)
        
        return result
    
    def create_gradient_gray_image(self, width, height, start_x=0, start_y=0, direction='vertical'):
        """
        创建一张从左到右 或从上到下 颜色逐渐变深的灰度图
        
        参数:
            width (int): 图片宽度
            height (int): 图片高度
            start_x (int): 起始x坐标
            start_y (int): 起始y坐标
            direction: horizontal(横) / vertical(竖)
        返回:
            PIL.Image: 生成的灰度图像
        """

        if direction == 'vertical':
            # 垂直 
            gradient = np.linspace(255, 0, height, dtype=np.uint8)
            gradient_array = np.tile(gradient, (width, 1)).T
        elif direction == 'horizontal':
            # 创建一个从255到0的线性渐变数组  横像
            gradient = np.linspace(255, 0, width, dtype=np.uint8) 
            # 将渐变数组扩展为二维图像数组
            gradient_array = np.tile(gradient, (height, 1))
        else:
            gradient = np.linspace(255, 0, height, dtype=np.uint8)
            gradient_array = np.tile(gradient, (width, 1)).T
        
        # 创建图像
        img = Image.fromarray(gradient_array, mode='L')
        
        # 如果需要从特定位置开始，可以创建一个更大的画布并粘贴
        if start_x > 0 or start_y > 0:
            canvas = Image.new('L', (start_x + width, start_y + height), color=255)
            canvas.paste(img, (start_x, start_y))
            return self.pil_to_cv2(canvas)[0:height, 0:width]
        else:
            return self.pil_to_cv2(img)
        
    def apply_gray_as_alpha_cv2(self, bgr_image, gray_image):
        """
        将灰度图的像素值作为 BGR(A) 图像的 alpha 通道（OpenCV 版本）
        
        参数:
            bgr_image (numpy.ndarray): BGR 或 BGRA 格式的图像（H×W×3 或 H×W×4）
            gray_image (numpy.ndarray): 单通道灰度图像（H×W）
        
        返回:
            numpy.ndarray: BGRA 格式的图像（H×W×4）
        """
        # 检查输入尺寸是否匹配
        if bgr_image.shape[:2] != gray_image.shape[:2]:
            print(f'bgr_image.shape[:2]-{bgr_image.shape[:2]}; gray_image.shape[:2]-{gray_image.shape[:2]}')
            raise ValueError("BGR(A) 图像和灰度图像的尺寸必须相同")
        
        # 确保灰度图是单通道 uint8
        if gray_image.ndim == 3:
            gray_image = cv2.cvtColor(gray_image, cv2.COLOR_BGR2GRAY)
        gray_image = gray_image.astype(np.uint8)
        
        # 处理 BGR / BGRA 输入
        if bgr_image.ndim == 2:  # 如果是灰度图，转 BGR
            bgr_image = cv2.cvtColor(bgr_image, cv2.COLOR_GRAY2BGR)
        elif bgr_image.shape[2] == 4:  # 如果是 BGRA，提取 BGR
            bgr_image = bgr_image[:, :, :3]
        elif bgr_image.shape[2] != 3:  # 如果不是 3 通道，报错
            raise ValueError("输入必须是 BGR 或 BGRA 格式")
        
        # 合并 BGR + Alpha 通道
        b, g, r = cv2.split(bgr_image)
        bgra_image = cv2.merge([b, g, r, gray_image])
        
        return bgra_image
    
    def dataframe_to_cv2_image(self, df, font_size=14, font_path=None, cell_padding=10, 
                          text_color=(10, 10, 10), bg_color=(240, 240, 240), 
                          header_color=(220, 220, 220), grid_color=(180, 180, 180)):
        """
        将 pandas.DataFrame 转换为 cv2 格式的图像
        
        参数:
            df: pandas.DataFrame - 要转换的数据框
            font_size: int - 字体大小 (默认14)
            font_path: str - 字体文件路径 (None为默认字体)
            cell_padding: int - 单元格内边距 (默认10)
            text_color: tuple - 文本颜色 (BGR格式，默认黑色)
            bg_color: tuple - 背景颜色 (BGR格式，默认白色)
            header_color: tuple - 表头颜色 (BGR格式，默认灰色)
            grid_color: tuple - 网格线颜色 (BGR格式，默认浅灰色)
        
        返回:
            numpy.ndarray - OpenCV格式的图像 (BGR)
        """
        # 确保数据是字符串格式
        df = df.astype(str)
        
        # 尝试加载中文字体 (如果指定)
        try:
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                # 尝试加载默认中文字体 (Windows)
                try:
                    font = ImageFont.truetype("simhei.ttf", font_size)
                except:
                    # 如果失败，使用默认字体
                    font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()

         # 计算每个单元格的宽度和高度
        col_widths = []
        for col in df.columns:
            max_len = max([self.get_text_size(font, str(x))[0] for x in df[col]] + [self.get_text_size(font, col)[0]])
            col_widths.append(max_len + 2 * cell_padding)
        
        row_heights = []
        for _, row in df.iterrows():
            max_height = max([self.get_text_size(font, str(x))[1] for x in row])
            row_heights.append(max_height + 2 * cell_padding)
        
        # 添加表头高度
        header_height = max([self.get_text_size(font, col)[1] for col in df.columns]) + 2 * cell_padding
        row_heights.insert(0, header_height)
        
        # 计算图像总尺寸
        total_width = sum(col_widths)
        total_height = sum(row_heights)
        
        # 创建PIL图像
        pil_img = Image.new("RGB", (total_width, total_height), bg_color)
        draw = ImageDraw.Draw(pil_img)
        
        # 绘制表格内容
        y = 0
        # 绘制表头
        x = 0
        for i, col in enumerate(df.columns):
            # 绘制表头背景
            draw.rectangle([x, y, x + col_widths[i], y + row_heights[0]], fill=header_color)
            # 绘制表头文本 (居中)
            text_width, text_height = self.get_text_size(font, col)
            draw.text((x + (col_widths[i] - text_width) // 2, y + (row_heights[0] - text_height) // 2), 
                    col, font=font, fill=text_color)
            x += col_widths[i]
        
        y += row_heights[0]
        
        # 绘制数据行
        for _, row in df.iterrows():
            x = 0
            for i, value in enumerate(row):
                # 绘制单元格背景
                draw.rectangle([x, y, x + col_widths[i], y + row_heights[1]], fill=bg_color)
                # 绘制单元格文本 (居中)
                text_width, text_height = self.get_text_size(font, value)
                draw.text((x + (col_widths[i] - text_width) // 2, y + (row_heights[1] - text_height) // 2), 
                        value, font=font, fill=text_color)
                x += col_widths[i]
            y += row_heights[1]
        
        # 绘制网格线
        # 水平线
        y = 0
        for h in row_heights:
            draw.line([0, y, total_width, y], fill=grid_color)
            y += h
        draw.line([0, y, total_width, y], fill=grid_color)  # 最后一条线
        
        # 垂直线
        x = 0
        draw.line([x, 0, x, total_height], fill=grid_color)
        for w in col_widths:
            x += w
            draw.line([x, 0, x, total_height], fill=grid_color)
        
        # 转换为OpenCV格式 (BGR)
        cv2_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        return cv2_img

    
    def get_text_size(self, font, text):
        # 计算文本尺寸的兼容性函数
        #  Pillow 9.0.0 或更高版本，它会使用新的 getbbox() 方法；如果是旧版本，则会继续使用 getsize()
        try:
            # 新版本Pillow (>=9.0.0)
            bbox = font.getbbox(text)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            # 旧版本Pillow (<9.0.0)
            return font.getsize(text)
        
    def ndarray_cover_alpha_color(self, cover_color, img_ndarray, direction='vertical') -> np.ndarray:
        """ 图片线性遮盖指定颜色
        参数:
            cover_color: BGR
            img_ndarray: cv2 图像数据
            direction:  horizontal(横) / vertical(竖)
        返回:
            numpy.ndarray: BGRA 格式的图像（H×W×4）
        """
        img_add_alpha = self.add_alpha(img_ndarray)     # 增加透明层
        width, height = self.width_height(img_add_alpha)
        # 创建 cover_color 图片
        color_alpha = self.create_image(width=width, height=height, color=(*cover_color, 255))
        # print('......color_alpha:', color_alpha)
        # 创建 创建一张从左到右 或从上到下 颜色逐渐变深的灰度图
        gradient_gray_image = self.create_gradient_gray_image(width=width, height=height, start_x=0, start_y=0, direction=direction)
        # gradient_gray_image 作为 color_alpha alpha 值
        gray_as_alpha_cv2 = self.apply_gray_as_alpha_cv2(bgr_image=color_alpha, gray_image=gradient_gray_image)

        ret_ndarray = self.blend_images(img1=img_add_alpha, img2=gray_as_alpha_cv2)
        return ret_ndarray

    def get_average_color(self, x, y, width, height, img_ndarray):
        """获取图片指定区域的 BGR 平均颜色
        
        Args:
            x (int): 区域左上角 x 坐标
            y (int): 区域左上角 y 坐标
            width (int): 区域宽度
            height (int): 区域高度
            img_ndarray: 图片ndarray数据
        
        Returns:
            tuple: (B, G, R) 平均颜色值 (0-255)
        """
        # 读取图片 (OpenCV 默认是 BGR 格式)
        # img = cv2.imread(image_path)
        # if img is None:
        #     raise ValueError("无法加载图片，请检查路径是否正确")
        
        # 检查区域是否超出图片边界
        h, w = img_ndarray.shape[:2]
        if x < 0 or y < 0 or x + width > w or y + height > h:
            raise ValueError("指定区域超出图片边界")
        
        # 提取指定区域 (BGR 格式)
        region = img_ndarray[y:y+height, x:x+width]
        
        # 计算 BGR 平均颜色
        avg_bgr = np.mean(region, axis=(0, 1)).astype(int)
        
        # 返回 (B, G, R) 元组
        return tuple(avg_bgr)[:3]
    
    def crop_transparent(self, image_array: np.ndarray) -> np.ndarray:
        """
        裁剪 np.ndarray 图片的完全透明区域（仅处理有 alpha 通道的 RGBA 图像）。

        参数:
            image_array (np.ndarray): 输入的图像数组，格式为 H x W x 4（RGBA）

        返回:
            np.ndarray: 裁剪后的图像数组；如果没有 alpha 通道则返回原图。
        """
        # 检查是否为 RGBA 图像
        if image_array.ndim != 3 or image_array.shape[2] != 4:
            print("不是带透明通道的图像，返回原图")
            return image_array

        alpha_channel = image_array[:, :, 3]
        non_transparent = alpha_channel > 0  # 找出非透明区域

        if not np.any(non_transparent):
            print("图像完全透明，返回空图")
            return image_array[0:0, 0:0, :]  # 返回空图像

        # 计算非透明区域的边界框
        rows = np.any(non_transparent, axis=1)
        cols = np.any(non_transparent, axis=0)
        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]

        # 裁剪图像
        cropped_image = image_array[y_min:y_max+1, x_min:x_max+1, :]
        return cropped_image
    
    def filter_alpha_imgs(self, imgs_path) -> list:
        # 如果有透明通道图片，只返回透明通道图
        alpha_images = []
        for img_p in imgs_path:
            if self.check_alpha(img_path=img_p):
                alpha_images.append(img_p)
        return alpha_images
    
    def convert_to_jpg(self, input_path, output_path=None, quality=98, overwrite=False):
        """
        图片转 jpg
        """
        if sys.platform == 'darwin':  # mac系统使用 sips 命令将图片转换为 JPG 格式
            result = self.convert_to_jpg_using_sips(input_path, output_path, quality, overwrite)
        else:
            result = self.convert_to_jpg_using_pillow(input_path, output_path, background_color=(255, 255, 255), optimize=True, overwrite=True)
        return result
    
    def convert_to_jpg_using_sips(self, input_path, output_path=None, quality=98, overwrite=True):
        """
        使用 macOS 的 sips 命令将图片转换为 JPG 格式
        支持: PNG, BMP, TIFF, JPEG, GIF 等常见格式
        
        Args:
            input_path (str): 输入文件路径
            output_path (str, optional): 输出文件路径。如果为None，则自动生成
            quality (int): JPEG质量 (1-100)
            overwrite (bool): 是否覆盖已存在的输出文件
        
        Returns:
            bool: 转换是否成功
        """
        try:
            # 检查输入文件是否存在
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"输入文件不存在: {input_path}")
            
            # 自动生成输出路径（如果未提供）
            if output_path is None:
                input_dir = os.path.dirname(input_path)
                input_name = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(input_dir, f"{input_name}.jpg")
            
            # 检查输出文件是否已存在
            if os.path.exists(output_path) and not overwrite:
                raise FileExistsError(f"输出文件已存在: {output_path}。请设置 overwrite=True 来覆盖")
            
            # 获取文件信息
            file_cmd = ['file', '-b', '--mime-type', input_path]
            file_result = subprocess.run(file_cmd, capture_output=True, text=True)
            mime_type = file_result.stdout.strip()
            
            # print(f"转换: {input_path} ({mime_type}) -> {output_path}")
            
            # 构建 sips 命令
            cmd = [
                'sips',
                '-s', 'format', 'jpeg',
                '-s', 'formatOptions', str(quality),
                '--out', output_path,
                input_path
            ]
            
            # 执行转换命令
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() or "未知错误"
                # 处理常见错误
                if "CMYK" in error_msg:
                    # print("警告: 检测到CMYK色彩空间，sips可能无法完美处理")
                    # 使用 convert_to_jpg_using_pillow 转换图片
                    result = self.convert_to_jpg_using_pillow(input_path, output_path, quality, background_color=(255, 255, 255), optimize=True, overwrite=True)
                    return result
                else:
                    raise RuntimeError(f"sips 转换失败: {error_msg}")
            
            # 验证输出文件
            if not os.path.exists(output_path):
                raise RuntimeError("输出文件未成功创建")
            
            # 计算压缩信息
            # input_size = os.path.getsize(input_path)
            # output_size = os.path.getsize(output_path)
            # compression_ratio = (output_size / input_size) * 100
            
            # print(f"✓ 转换成功!")
            # print(f"  文件大小: {input_size / 1024:.1f} KB → {output_size / 1024:.1f} KB")
            # print(f"  压缩比例: {compression_ratio:.1f}%")
            
            return True
            
        except subprocess.TimeoutExpired:
            print("✗ 转换超时，文件可能过大或损坏")
            return False
        except Exception as e:
            print(f"✗ 转换失败: {e}")
            # 清理可能创建的不完整输出文件
            if output_path and os.path.exists(output_path):
                os.remove(output_path)
            return False
        
    def convert_to_jpg_using_pillow(self, input_path, output_path=None, quality=98, 
                               background_color=(255, 255, 255), optimize=True, overwrite=False):
        """
        使用 Pillow 库将图片转换为 JPG 格式
        支持更广泛的格式和特殊处理
        
        Args:
            input_path (str): 输入文件路径
            output_path (str, optional): 输出文件路径
            quality (int): JPEG质量 (1-100)
            background_color (tuple): 透明背景的填充颜色 (R, G, B)
            optimize (bool): 是否进行优化压缩
            overwrite (bool): 是否覆盖已存在的输出文件
        
        Returns:
            bool: 转换是否成功
        """
        try:
            # 检查输入文件
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"输入文件不存在: {input_path}")
            
            # 自动生成输出路径
            if output_path is None:
                input_dir = os.path.dirname(input_path)
                input_name = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(input_dir, f"{input_name}.jpg")
            
            # 检查输出文件
            if os.path.exists(output_path) and not overwrite:
                raise FileExistsError(f"输出文件已存在: {output_path}")
            
            # 打开图像
            with Image.open(input_path) as img:
                original_mode = img.mode
                original_size = img.size
                original_format = img.format
                
                # print(f"转换: {input_path} ({original_format}, {original_mode}) -> {output_path}")
                
                # 处理不同的图像模式
                if original_mode in ('RGBA', 'LA', 'PA'):
                    # 处理带透明度的图像
                    print(f"  检测到透明度通道 ({original_mode})，使用背景色 {background_color} 填充")
                    
                    if original_mode == 'P':
                        # 调色板模式先转换为RGBA
                        img = img.convert('RGBA')
                    
                    # 创建背景并合并
                    background = Image.new('RGB', img.size, background_color)
                    if hasattr(img, 'getchannel') and 'A' in img.getbands():
                        # 使用alpha通道作为蒙版
                        background.paste(img, mask=img.getchannel('A'))
                    else:
                        background.paste(img)
                    img = background
                    
                elif original_mode == 'CMYK':
                    # CMYK色彩空间转换
                    print("  检测到CMYK色彩空间，转换为RGB")
                    img = img.convert('RGB')
                    
                elif original_mode not in ('RGB', 'L'):
                    # 其他模式统一转换
                    print(f"  转换模式: {original_mode} -> RGB")
                    img = img.convert('RGB')
                
                # 处理16位图像
                if hasattr(img, 'bits') and getattr(img, 'bits', 8) == 16:
                    print("  检测到16位图像，转换为8位")
                    if img.mode == 'I;16':
                        img = img.point(lambda i: i * (1 / 256)).convert('L')
                    elif img.mode == 'I;16B':
                        img = img.point(lambda i: i * (1 / 256)).convert('L')
                    else:
                        img = img.convert('RGB')
                
                # 保存前的元数据
                input_size_bytes = os.path.getsize(input_path)
                
                # 保存为JPEG
                save_params = {
                    'quality': quality,
                    'optimize': optimize,
                    'subsampling': '4:4:4' if quality > 90 else '4:2:0'
                }
                
                img.save(output_path, 'JPEG', **save_params)
            
            # 计算压缩信息
            output_size_bytes = os.path.getsize(output_path)
            compression_ratio = (output_size_bytes / input_size_bytes) * 100
            
            print(f"✓ 转换成功!")
            print(f"  原始尺寸: {original_size}, 模式: {original_mode}")
            print(f"  文件大小: {input_size_bytes / 1024:.1f} KB → {output_size_bytes / 1024:.1f} KB")
            print(f"  压缩比例: {compression_ratio:.1f}%")
            
            return True
            
        except Exception as e:
            print(f"✗ 转换失败: {e}")
            # 清理可能创建的不完整文件
            if output_path and os.path.exists(output_path):
                os.remove(output_path)
            return False
        

if __name__ == '__main__':
    # run: python zwutils_methods/img_handle.py
    cls_imghandle = ImgHandle()    # 图片基本操作

    img_path = '/Users/senmalay/v_programs/tb_goods_pump/y2025/deep_well_pump/dwp_d324_t130qj8/details/d_461.jpeg'
    # print('Path', img_path)
    # img_ndarray = cls_imghandle.img_to_ndarray(img_path=img_path)
    # # print(img_ndarray)
    # resized_ndarray = cls_imghandle.resize_ndarray((750, 1000), img_ndarray)


    # test put_text_with_word_wrap()
#     font_path = '/Users/senmalay/v_programs/dev/self_apps/pump_taobao_handle/confs/fonts_zh/SimHei.ttf'
#     long_text = """快递签收:
# 物流难免会磕碰，签收前请当着快递员的面，验收货物完好后再收货。如发现产品破损、少件，请拒收或联系客服。签收会默认视为产品无问题，因而签收后再发现破损无法得到补偿。
# 产品质保：
# 1. 产品官方10年质保，1年内质量问题换新，1年后免费维修或折旧换新。（保修仅需下单产生的订单编号）
# 2. 自订单签收后，一年内有质量问题（人为除外）可免费换新一次（同型号），运费各自承担。
# 非质量问题，人为原因造成，买家需要另外承担相应费用。
# 3. 购买订单签收一年后，折旧换新或免费维修（买家承担来回邮费）
# 4. 折旧计算：使用1-2年折I日50%（剩余价值50%）2-4年折I日70%（剩余价值30%）超过4年-终身折旧85%（剩余价值15%）。
# 5. 保修仅限于泵内部（电机）其它易损件和磨损件不在内。例如：多级叶轮、螺杠叶轮、碳刷、提手、网罩、电源线、压力开关、压力罐、电容、水流传感器，线路板等⋯容易磕碰和磨损的物件。（质保期为三个月）
# 6. 退换货商品需要保持原状，如客户私自改装、剪断电源线的插头等，影响二次销售则不支持退货。
# 服务时效：
# """
#     # long_text = "这是一段很长很长的文本，它将根据指定的宽度自动换行。OpenCV的putText函数本身不支持自动换行，但这个函数解决了这个问题。现在中文可以正确显示了！"
#     bg_img = cls_imghandle.create_image(900, 1200, (0, 0, 0, 0))
#     test_result, w, h = cls_imghandle.put_text_multiline(
#         image=bg_img, text=long_text, position=(50, 50), font_path=font_path, font_size=24, color=(20, 20, 20, 255),
#         line_spacing=1.5, max_width=800, paragraph_spacing=1.2
#     )
#     test_result_write_path = '/Users/senmalay/v_programs/dev/self_apps/pump_taobao_handle/temp_files/test_write_wrods.png'
#     cls_imghandle.ndarray_to_img(img=test_result, write_path=test_result_write_path)

    # 拼接图片
    dir_path = '/Users/senmalay/Downloads/1688-extension/concat_imgs'
    concatenate_ndaray = cls_imghandle.concatenate_imgs_in_dir(dir_path)
    from pathlib import Path
    save_path = Path(dir_path) / 'concatenate.jpg'
    cls_imghandle.ndarray_to_img(concatenate_ndaray, str(save_path))
    print(f'save_path: {str(save_path)}')

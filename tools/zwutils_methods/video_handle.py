import os
import shutil
from pathlib import Path
# import numpy as np
# from PIL import Image, ImageDraw, ImageFont
import copy
import subprocess
import tempfile
import json
import random
# 图片基本操作


class VideoHandle(object):
    """
    from zwutils_methods import VideoHandle    # 图片基本操作
    # self.cls_videohandle = VideoHandle()    # 视频基本操作
    """
    def __init__(self):
        pass
    
    def remove_video_metadata(self, input_file, output_file=None):
        """
        使用FFmpeg删除视频元数据
        :param input_file: 输入视频文件路径
        :param output_file: 输出视频文件路径
        """
        if output_file is None:
            input_file_name = Path(input_file).name
            dir_of_file = Path(input_file).resolve().parent
            temp_file = str(dir_of_file / f'tempxxxxx_file_{input_file_name}')
        else:
            temp_file = copy.deepcopy(output_file)

        command = [
            'ffmpeg',
            '-i', input_file,
            '-map_metadata', '-1',  # 删除所有元数据
            '-c:v', 'copy',         # 复制视频流，不重新编码
            '-c:a', 'copy',         # 复制音频流，不重新编码
            temp_file
        ]
        subprocess.run(command, check=True)

        if output_file is None:
            os.remove(input_file)
            shutil.move(temp_file, input_file)
        return output_file if output_file is not None else input_file
    
    def get_videos_paths_in_dir(self, folder_path):
        '''
        获取指定目录下的所有图片路径
        :param dir_path: 图片所在的目录
        :return: list
        '''
        # 检查文件夹是否存在且是一个目录
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            raise FileNotFoundError("The specified folder does not exist.")
        
        video_paths = []
        
        # 遍历文件夹中的每一个文件和子目录
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            # 确保处理的是文件而不是子目录
            if os.path.isfile(file_path):
                
                # 检查是否是视频
                if self.is_video_file(file_path):
                    video_paths.append(file_path)
        
        # 对路径列表进行排序
        video_paths.sort()
        
        return video_paths
    
    def is_video_file(self, file_path):
        """
        判断给定路径是否是视频文件
        
        参数:
            file_path (str/Path): 文件路径
            
        返回:
            bool: 如果是视频返回True，否则返回False
        """
        # 转换为Path对象以便处理路径
        file_path = Path(file_path)
        
        # 首先检查文件是否存在且是文件
        if not file_path.is_file():
            return False
        
        VIDEO_EXTENSIONS = {
            '.mp4','.mov','.avi','.mkv','.flv','.wmv','.webm','.mpg','.mpeg','.m4v'
        }
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in VIDEO_EXTENSIONS:
            return False
        
        # 使用ffprobe(FFmpeg的一部分)来检测文件是否是视频
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_type',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(file_path)
            ]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            # 如果输出中包含'video'，则认为是视频文件
            return result.stdout.strip() == 'video'
            
        except subprocess.CalledProcessError:
            # ffprobe执行失败，可能不是视频文件
            return False
        except FileNotFoundError:
            raise Exception("ffprobe not found. Please ensure FFmpeg is installed and in your PATH.")

    def get_video_dimensions(self, video_path):
        """
        使用 ffprobe 获取视频的宽度和高度。

        参数：
            video_path (str): 视频文件的路径。

        返回：
            tuple: (宽度, 高度)，如果发生错误则返回 None。
        """
        # 检查文件是否存在
        if not os.path.isfile(video_path):
            print('Error: video file not found')
            return None, None
    
        try:
            command = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "json",
                video_path,
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)
            stream = info.get("streams", [{}])[0]
            width = stream.get("width")
            height = stream.get("height")

            if width is None or height is None:
                print("未能解析出 width/height")
                return None, None

            return width, height
        except Exception as e:
            print(f"获取视频尺寸时发生错误：{e}")
            return None, None
        
    def compute_output_video_path(self, input_video_path, crop_width_or_start_seconds, crop_height_or_end_seconds, output_video_path = None) -> str:
        # 计算保存文件路径
        if output_video_path is not None:
            return output_video_path
        else:
            video_suffix = Path(input_video_path).suffix
            video_name_no_suffix = Path(input_video_path).stem
            output_name = f"{video_name_no_suffix}_{crop_width_or_start_seconds}_{crop_height_or_end_seconds}{video_suffix}"
            output_path = Path(input_video_path).parent / output_name
            return str(output_path)
        
    def scale_video(self, input_path, output_path, width=None, height=None, 
                keep_aspect_ratio=True, scale_algorithm='bicubic', 
                overwrite=True, ffmpeg_path='ffmpeg'):
        """
        使用FFmpeg缩放视频
        
        参数:
            input_path (str): 输入视频文件路径
            output_path (str): 输出视频文件路径
            width (int, optional): 目标宽度(像素)
            height (int, optional): 目标高度(像素)
            keep_aspect_ratio (bool): 是否保持宽高比(默认True)
            scale_algorithm (str): 缩放算法(默认'bicubic')
                                可选: 'fast_bilinear', 'bilinear', 'bicubic',
                                    'experimental', 'neighbor', 'area', 'bicublin', 'gauss', 'sinc',
                                    'lanczos', 'spline'
            overwrite (bool): 是否覆盖已存在的输出文件(默认True)
            ffmpeg_path (str): FFmpeg可执行文件路径(默认'ffmpeg')
        
        返回:
            bool: 操作是否成功
        """
        # 检查FFmpeg是否可用
        if not shutil.which(ffmpeg_path):
            raise FileNotFoundError(f"FFmpeg executable '{ffmpeg_path}' not found")
        
        # 构建基本命令
        cmd = [ffmpeg_path, '-i', input_path]
        
        # 添加覆盖选项
        if overwrite:
            cmd.append('-y')
        else:
            cmd.append('-n')
        
        # 构建缩放过滤器
        scale_filter = []
        
        # 设置目标分辨率
        if width and height:
            if keep_aspect_ratio:
                scale_filter.append(f'scale=w={width}:h={height}:force_original_aspect_ratio=decrease')
                scale_filter.append(f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2')
            else:
                scale_filter.append(f'scale={width}:{height}')
        elif width:
            scale_filter.append(f'scale={width}:-2')
        elif height:
            scale_filter.append(f'scale=-2:{height}')
        else:
            raise ValueError("Either width or height must be specified")
        
        # 添加缩放算法
        if scale_algorithm:
            scale_filter[-1] += f':flags={scale_algorithm}'
        
        # 添加视频过滤器选项
        cmd.extend(['-vf', ','.join(scale_filter)])
        
        # 保持原始编码质量
        cmd.extend(['-c:a', 'copy'])  # 保持音频不变
        cmd.extend(['-c:v', 'libx264', '-preset', 'slow', '-crf', '18'])  # 高质量H.264编码
        
        # 添加输出路径
        cmd.append(output_path)
        
        try:
            # 运行FFmpeg命令
            subprocess.run(cmd, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg command failed with error: {e.stderr.decode('utf-8')}")
            return False
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False
        
    def crop_video(self, input_video_path, crop_width, crop_height, start_x = None, start_y = None, output_video_path = None):
        # 裁剪视频
        output_video = self.compute_output_video_path(input_video_path, crop_width, crop_height, output_video_path)

        try:
            # with VideoFileClip(mp4_path) as video:
            #     # 获取原始视频的尺寸
            #     original_width, original_height = video.size
            original_width, original_height = self.get_video_dimensions(input_video_path)     # 获取原始视频的尺寸
            if original_width is None or original_height is None:
                print('ErrorCompute video original size(width, height):', original_width, original_height)
                return
            if original_width >= crop_width and original_height >= crop_height:
                # 计算裁剪区域的左上角坐标，使其居中
                offset_x = (original_width - crop_width) // 2
                offset_y = (original_height - crop_height) // 2
                # 制定开始裁剪位置
                if start_x is not None and start_y is not None:
                    offset_x = start_x
                    offset_y = start_y
                # x2 = x1 + crop_width
                # y2 = y1 + crop_height

                ffmpeg_command = [
                    "ffmpeg",
                    "-y", "-i", input_video_path,
                    "-vf", f"crop={crop_width}:{crop_height}:{offset_x}:{offset_y}",
                    output_video
                ]

                subprocess.run(ffmpeg_command, check=True)
            else:
                print(f'Error_CropSize invalid width_height(source_mp4_width_height:[{original_width}, {original_height}], target_width_height:[{crop_width}, {crop_height}])......')

        except FileNotFoundError:
            print(f"crop_video.错误: 文件 {input_video_path} 未找到。")
        except ValueError as ve:
            print(f"crop_video.参数错误: {ve}")
        except Exception as e:
            print(f"crop_video.发生错误: {e}")
        finally:
            return output_video
        
    def extract_last_frame(self, video_path, output_image_path):
        """
        使用 ffmpeg 截取视频的最后一帧并保存为图像

        :param video_path: 输入视频文件路径
        :param output_image_path: 输出图像文件路径（如 output.jpg）; .png 为无损格式
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        # ffmpeg 命令：先查视频时长，再取最后一帧
        cmd = [
            "ffmpeg",
            "-sseof", "-1",          # 从倒数第1秒开始读取
            "-i", video_path,        # 输入文件
            "-vframes", "1",         # 只截取1帧
            output_image_path,       # 输出图片路径
            "-y"                     # 覆盖输出
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"成功提取最后一帧到: {output_image_path}")
            return True
        except subprocess.CalledProcessError as e:
            # raise RuntimeError(f"ffmpeg 运行失败: {e}")
            print(f"ffmpeg 运行失败: {e}")
            return False
        
    def extract_first_frame(self, video_path, output_image_path):
        """
        使用 ffmpeg 提取视频的第一帧并保存为图片。

        参数:
            video_path (str): 输入视频文件路径。
            output_image_path (str): 输出图片文件路径。

        返回:
            bool: True 表示成功，False 表示失败。
        """
        if not os.path.isfile(video_path):
            print(f"错误：视频文件不存在 -> {video_path}")
            return False

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_image_path), exist_ok=True)

        # ffmpeg 命令：提取第一帧
        command = [
            "ffmpeg",
            "-y",                  # 覆盖输出文件
            "-i", video_path,
            "-frames:v", "1",      # 只提取一帧
            "-q:v", "2",           # 输出质量（对 JPEG 有效，1 是最好，31 是最差）
            output_image_path
        ]

        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"第一帧已保存到: {output_image_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"提取第一帧失败: {e.stderr.decode().strip()}")
            return False
        
    def concat_videos_in_folder(self, folder_path, output_path, video_extensions=('.mp4', '.mov', '.mkv')):
        """
        使用 ffmpeg 拼接文件夹内的视频为一个输出文件

        :param folder_path: 视频所在文件夹路径
        :param output_path: 输出拼接后的视频文件路径（如 output.mp4）
        :param video_extensions: 要拼接的视频扩展名元组，默认包含常见格式
        """
        # 获取视频文件（排序以确保顺序一致）
        video_files = sorted([
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(video_extensions)
        ])

        if not video_files:
            raise ValueError("文件夹中未找到可拼接的视频文件")

        # 创建 ffmpeg 需要的 concat list 文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt") as list_file:
            for path in video_files:
                # ffmpeg concat 要求使用 file '路径'
                list_file.write(f"file '{os.path.abspath(path)}'\n")
            list_file_path = list_file.name

        # 使用 ffmpeg concat 模式拼接
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file_path,
            "-c", "copy",
            output_path,
            "-y"  # 覆盖输出文件
        ]

        try:
            subprocess.run(cmd, check=True)
            print(f"成功拼接视频到: {output_path}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ffmpeg 拼接失败: {e}")
        finally:
            os.remove(list_file_path)

    def resize_video(self, input_path, output_path, target_width, target_height):
        """
        使用 ffmpeg 缩放视频为指定尺寸，保持比例并居中裁剪（不会变形）

        参数:
            input_path (str): 输入视频路径
            output_path (str): 输出视频路径
            target_width (int): 目标宽度（如 1080）
            target_height (int): 目标高度（如 720）
        """
        filter_str = (
            f"scale='if(gt(a,{target_width}/{target_height}),{target_height}*a,{target_width})':"
            f"'if(gt(a,{target_width}/{target_height}),{target_height},{target_width}/a)',"
            f"crop={target_width}:{target_height}"
        )

        command = [
            'ffmpeg', '-y',
            '-i', input_path,
            '-vf', filter_str,
            '-c:a', 'copy',
            output_path
        ]

        try:
            subprocess.run(command, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 视频处理失败: {e}")
            return False

    def trim_media_by_ms(self, input_path, output_path, start_ms, end_ms):
        """
        使用 ffmpeg 截取视频或音频片段（单位：毫秒）

        参数：
            input_path (str): 原始媒体文件路径（支持视频和音频）
            output_path (str): 输出文件路径
            start_ms (int): 开始时间（毫秒）
            end_ms (int): 结束时间（毫秒）

        返回：
            bool: 是否成功截取
        """
        if not os.path.isfile(input_path):
            print("错误：找不到输入文件")
            return False

        if start_ms < 0 or end_ms <= start_ms:
            print("错误：开始时间和结束时间无效")
            return False

        # 计算持续时间（毫秒）
        duration_ms = end_ms - start_ms

        # 转换为秒（小数）
        start_sec = start_ms / 1000.0
        duration_sec = duration_ms / 1000.0

        try:
            cmd = [
                "ffmpeg",
                "-y",  # 自动覆盖输出文件
                "-ss", f"{start_sec:.3f}",
                "-i", input_path,
                "-t", f"{duration_sec:.3f}",
                "-c", "copy",  # 不重新编码，快速截取
                output_path
            ]
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print("ffmpeg 执行失败:", e)
            return False
        
    def split_video_to_frames(self, video_path, output_dir, image_format='png', fps=None):
        """
        使用 ffmpeg 将视频拆分为图片帧。

        参数:
            video_path (str): 输入视频文件路径。
            output_dir (str): 输出图片帧保存的文件夹。
            image_format (str): 图片格式，如 'png', 'jpg'。默认 'png'。
            fps (float or int): 如果设置，按指定帧率提取帧。例如 fps=1 表示每秒一帧。
        """
        if not os.path.isfile(video_path):
            # raise FileNotFoundError(f"视频文件不存在: {video_path}")
            print(f"视频文件不存在: {video_path}")
            return False
        
        os.makedirs(output_dir, exist_ok=True)

        output_pattern = os.path.join(output_dir, f"frame_%05d.{image_format}")
        cmd = ["ffmpeg", "-i", video_path]

        if fps:
            cmd += ["-vf", f"fps={fps}"]

        cmd += [output_pattern]

        try:
            subprocess.run(cmd, check=True)
            print(f"视频帧已保存到：{output_dir}")
            return True
        except subprocess.CalledProcessError as e:
            print("ffmpeg 执行失败:", e)
            return False

    def images_to_video(self, image_dir, output_video_path, fps=30, image_format='png', resolution=None):
        """
        使用 ffmpeg 将指定文件夹中的图片合成为视频。

        参数:
            image_dir (str): 图片所在文件夹路径。
            output_video_path (str): 输出视频文件路径（例如 output.mp4）。
            fps (int): 视频帧率，默认 30。
            image_format (str): 图片格式，例如 'png' 或 'jpg'。
            resolution (tuple): (宽, 高)，可选，强制输出为该分辨率。
        """
        if not os.path.isdir(image_dir):
            # raise FileNotFoundError(f"图片文件夹不存在: {image_dir}")
            print(f"--- Error --- 图片文件夹不存在: {image_dir}")
            return False

        # 图片命名必须是连续序号，比如 frame_00001.png、frame_00002.png ...
        input_pattern = os.path.join(image_dir, f"frame_%05d.{image_format}")
        
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", input_pattern,
        ]

        if resolution:
            width, height = resolution
            cmd += ["-vf", f"scale={width}:{height}"]

        cmd += [
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",  # 保证兼容性
            output_video_path
        ]

        try:
            subprocess.run(cmd, check=True)
            # print(f"视频生成成功: {output_video_path}")
            return True
        except subprocess.CalledProcessError as e:
            print("Error ffmpeg 执行失败:", e)
            return False

    def get_media_duration_ms(self, video_path):
        """
        获取音频, 视频的时长（毫秒）。
        
        参数：
            video_path (str): 视频文件的路径。
            
        返回：
            int: 视频时长（单位：毫秒）。如果失败返回 None。
        """
        if not os.path.isfile(video_path):
            print("错误：找不到视频文件")
            return None

        try:
            # 使用 ffprobe 获取时长（单位：秒）
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "json",
                    video_path
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            info = json.loads(result.stdout)
            duration_sec = float(info["format"]["duration"])
            return int(duration_sec * 1000)  # 转换为毫秒

        except Exception as e:
            print("获取视频长度失败：", e)
            return None
        
    def get_all_audio_files(self, folder_path, extensions=None):
        """
        获取文件夹内所有音频文件路径

        参数：
            folder_path (str): 目标文件夹路径
            extensions (list): 可选，指定的音频扩展名列表（不区分大小写），默认常见音频格式

        返回：
            list: 所有音频文件的完整路径列表
        """
        if extensions is None:
            extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma']

        audio_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in [e.lower() for e in extensions]:
                    audio_files.append(os.path.join(root, file))

        return audio_files
    
    def replace_video_audio(self, video_path, audio_path, output_path, ffmpeg_path='ffmpeg') -> bool:
        """
        使用FFmpeg替换视频文件的音频
        
        参数:
            video_path (str): 原始视频文件路径
            audio_path (str): 新音频文件路径
            output_path (str): 输出文件路径
            ffmpeg_path (str): FFmpeg可执行文件路径(默认在PATH中查找)
        
        返回:
            bool: 操作是否成功
        """
        try:
            # 构建FFmpeg命令
            command = [
                ffmpeg_path,
                '-y',  # 自动覆盖输出文件
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',  # 复制视频流，不重新编码
                '-map', '0:v:0',  # 选择第一个输入的视频流
                '-map', '1:a:0',  # 选择第二个输入的音频流
                '-shortest',  # 以最短的输入流为准
                output_path
            ]
            
            # 运行FFmpeg命令
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg命令执行失败: {e}")
            return False
        except Exception as e:
            print(f"发生错误: {e}")
            return False
    
    def add_audio_to_video(self, video_path, audio_path, output_path) -> bool:
        """
        使用 ffmpeg 给视频添加音频轨道（将原视频的音轨替换为指定音频）

        参数：
            video_path (str): 视频文件路径
            audio_path (str): 音频文件路径
            output_path (str): 输出文件路径（带后缀）

        返回：
            bool: 是否成功
        """
        if not os.path.isfile(video_path):
            print("错误：视频文件不存在")
            return False
        if not os.path.isfile(audio_path):
            print("错误：音频文件不存在")
            return False

        try:
            cmd = [
                "ffmpeg",
                "-y",  # 覆盖输出
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",     # 保留视频流
                "-c:a", "aac",      # 音频编码为 AAC（兼容性好）
                "-map", "0:v:0",    # 选取第一个视频流
                "-map", "1:a:0",    # 选取音频文件中的第一个音轨
                "-shortest",        # 输出文件时长 = 较短的那一个
                output_path
            ]
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print("ffmpeg 执行失败:", e)
            return False
        
    def get_video_frame_count(self, video_path):
        """
        获取视频的总帧数

        参数:
            video_path (str): 视频文件路径

        返回:
            int: 视频总帧数，获取失败时返回 None
        """
        if not os.path.isfile(video_path):
            print("错误：找不到视频文件")
            return None

        command = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-count_frames",
            "-show_entries", "stream=nb_read_frames",
            "-of", "default=nokey=1:noprint_wrappers=1",
            video_path
        ]

        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            frame_count = int(result.stdout.strip())
            return frame_count
        except subprocess.CalledProcessError as e:
            print("ffprobe 执行出错:", e.stderr)
            return None
        except ValueError:
            print("无法解析帧数:", result.stdout)
            return None
        
    def random_get_bg_music(self, audios_dir_path, tmp_dir_path, video_path):
        # 随机获取背景音乐
        video_length = self.get_media_duration_ms(video_path)
        audio_path = None
        loop_count = 0
        while audio_path is None and loop_count < 2000:
            audios_files_list = self.get_all_audio_files(audios_dir_path, extensions=None)
            current_audio_path = random.choice(audios_files_list)
            current_audio_length = self.get_media_duration_ms(current_audio_path)
            if current_audio_length >= video_length:
                audio_path = current_audio_path
            loop_count += 1

        if audio_path is None:
            print('Error: No valid audio file...')
            return None   # 没有适合的音频文件
        # 截取背景音乐
        trim_audio = self._random_trim_bg_music(tmp_dir_path, audio_path, video_length)
        return trim_audio
    
    def _random_trim_bg_music(self, tmp_dir_path, audio_path, video_length):
         # 随机截取背景音乐
        audio_length = self.get_media_duration_ms(audio_path)
        start_time = random.randint(0, int(audio_length - video_length))
        output_audio_path = self._path_tmp_bg_music_path(tmp_dir_path, audio_path)
        result = self.trim_media_by_ms(input_path=audio_path, output_path=output_audio_path, start_ms=start_time, end_ms=start_time + video_length)
        return output_audio_path if result else None
    
    def _path_tmp_bg_music_path(self, tmp_dir_path, audio_path):
        # 临时保存的背景音乐路径
        tmp_bg_music_dir_path = Path(tmp_dir_path) / f'tmp_trim_{Path(audio_path).name}'
        return str(tmp_bg_music_dir_path)

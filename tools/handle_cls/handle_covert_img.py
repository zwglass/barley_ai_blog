from pathlib import Path
from nanoid import generate      # pip install nanoid
from zwutils_methods import ImgHandle    # 图片基本操作


class HandleConvertImg(object):
    """
    from handle_cls import HandleConvertImg     # 图片转换操作
    #    self.cls_handle_convert_img = HandleConvertImg()     # 图片转换操作
    """
    def __init__(self, cls_main_params):
        self.cls_main_params = cls_main_params
        self.path_tmp_dir = cls_main_params.glob_confs.get_config('path_tmp_dir')
        self.cls_imghandle = ImgHandle()    # 图片基本操作

    def main_to_jpg(self, images_paths=None, dir_path=None, prefix=None, to_svg=False):
        # 图片转 jpg
        out_dirs = []
        out_dir1 = self.handle_convert_images(images_paths=images_paths, out_dir=None, to_svg=to_svg)
        out_dir2 = self.handle_convert_imgs_in_dir(dir_path=dir_path, prefix=prefix)
        if out_dir1 is not None:
            out_dirs.append(out_dir1)
        if out_dir2 is not None:
            out_dirs.append(out_dir2)
        return out_dirs

    def handle_convert_images(self, images_paths=None, out_dir=None, to_svg=False):
        # 根据图片路径批量转换
        if not isinstance(images_paths, list):
            return None
        if out_dir is None:
            write_dir_path = Path(self.path_tmp_dir) / 'convert_imgs' / f'{self.cls_main_params.date_prefix}_{generate(size=4)}'
        else:
            write_dir_path = Path(out_dir)
        write_dir_path.mkdir(parents=True, exist_ok=True)

        for img_path in images_paths:
            current_save_path = write_dir_path / f'{Path(img_path).stem}.jpg'
            if to_svg:    # 保存为 svg
                current_save_svg_path = write_dir_path / f'{Path(img_path).stem}.svg'
                self.cls_imghandle.img_to_svg(source_img_path=img_path, output_path=str(current_save_svg_path))

            img_ndarr = self.cls_imghandle.img_to_ndarray(img_path)
            self.cls_imghandle.ndarray_to_img(img_ndarr, write_path=str(current_save_path))
        return str(write_dir_path)
    
    def handle_convert_imgs_in_dir(self, dir_path=None, prefix=None, to_svg=False):
        if not isinstance(dir_path, str) or not Path(dir_path).is_dir():
            return None
        
        imgs_paths = self.cls_imghandle.get_imgs_paths_in_dir(folder_path=dir_path, prefix=prefix, to_svg=to_svg)
        out_dir = Path(self.path_tmp_dir) / 'convert_imgs' / Path(dir_path).name
        return self.handle_convert_images(images_paths=imgs_paths, out_dir=str(out_dir))
        
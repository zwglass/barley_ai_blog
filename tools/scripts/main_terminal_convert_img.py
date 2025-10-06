from main_params import cls_main_params      # 操作的文件夹,统一入口; 修改 main_terminal_params.py 的参数.
from handle_cls import HandleConvertImg     # 图片转换操作


if __name__ == '__main__':
    # run: python tools/scripts/main_terminal_convert_img.py
    # 图片转换为 .jpg

    # ------ 修改参数 ------
    images_paths = [
        '/Users/senmalay/v_programs/dev/github_projects/barley_ai_blog/data/logo_white.png',
    ]

    cls_handle_convert_img = HandleConvertImg(cls_main_params)     # 图片转换操作
    results = cls_handle_convert_img.main_to_jpg(images_paths, to_svg=True)

    print('Converted imgs dirs:', results)

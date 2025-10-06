from pathlib import Path
import base64
import requests
import json
import uuid
import copy
import time
from io import BytesIO
from PIL import Image     # pip install pillow


class ComfyApiHandle(object):
    """
    from zwutils_methods import ComfyApiHandle    # comfyui api
    # self.cls_comfy_api = ComfyApiHandle()    # comfyui api
    """
    def __init__(self):
        pass

    def main_image_inference(self, img_path, comfyui_api_prompt:dict, node_idx="80", input_key='image', base_url: str = "http://localhost:8188", generated_img_output_dir = None, write_img_keys = None):
        """
        主函数, 图片重绘
        write_img_keys (tuple<str>): 保存图片的idx, None 全部保存
        """
        if not self._check_upload_img(img_path):
            print('Image Path Error...', img_path)
            return None
                  
        uploaded_img_name = self.upload_img(img_path, base_url=base_url)
        if uploaded_img_name is None:
            print('uploaded img Failed...')
            return None
        
        updated_prompt = self.comfyui_prompt_update_value(node_idx=node_idx, input_key=input_key, new_value=uploaded_img_name, comfyui_api_prompt=comfyui_api_prompt)
        
        result = self.api_run(updated_prompt, base_url=base_url)
        image_name_no_suffix = Path(img_path).stem

        write_imgs_path = []
        if result is not None:
            for k, images in result.items():
                # print(f'inference k: {k}')
                if write_img_keys is not None and k not in write_img_keys:
                    continue   # 不保存图片

                for idx, img_bytes in enumerate(images):
                    write_path = self.write_temp_png_path(f"{image_name_no_suffix}_{k}_{idx}", generated_img_output_dir)
                    self.bytes_to_image(img_bytes, write_path)    # 保存图片
                    write_imgs_path.append(write_path)
                    # print(f'Image key: {k}_{idx}; write path: {write_path}', 'write path:')

        return write_imgs_path


    def upload_img(self, img_path, base_url: str = "http://localhost:8188"):
        """
        将本地文件上传至服务器
        """
        with open(img_path, 'rb') as f:
            upload_response = requests.post(
                f"{base_url}/upload/image",
                files={"image": f}
            )
            if upload_response.status_code == 200:
                new_image_filename = upload_response.json()['name']
                return new_image_filename
            else:
                print(f"上传图片失败，{upload_response}")
                return None
            
    def api_run(self, comfyui_api_prompt:dict, base_url: str = "http://localhost:8188"):
        """
        执行 compyui 的 API 接口
        """
        url = f"{base_url}/api/prompt"
        # 提交请求运行工作流
        api_dict = {"prompt": comfyui_api_prompt, "client_id": str(uuid.uuid4())}
        # data = json.dumps().encode('utf-8')
        response = requests.post(url, json=api_dict)

        # 返回包含 prompt_id 的响应
        # print("StatusCode:", response.status_code)
        res_json = response.json()
        # print("Response:", res_json)
        prompt_id = res_json.get('prompt_id', None)
        if prompt_id is None:
            print(f"API运行失败，返回的 prompt id 为：{prompt_id}")
            return None
        
        history = self.wait_for_completion(base_url, prompt_id, poll_interval=2)
        if history is None:
            return None
        
        images = self.get_images(base_url, history)
        
        return images

    def wait_for_completion(self, server_url, prompt_id, poll_interval=2):
        loop_count = 0
        while loop_count < 1000:
            try:
                response = requests.get(f"{server_url}/history/{prompt_id}")
                history = response.json()
                if prompt_id in history:  # 任务完成时，历史记录会更新
                    # print(f'Inference use Time {loop_count} count.')
                    return history[prompt_id]
                time.sleep(poll_interval)  # 避免频繁请求
                loop_count += 1
            except Exception as e:
                print(f'--- Error:  Requests failed (FailedCount:{loop_count}) {server_url} ...')
                print(e)
                time.sleep(poll_interval)  # 避免频繁请求
                loop_count += 1
        return None

    def get_images(self, server_url, history):
        output_images = {}
        for node_id, node_output in history["outputs"].items():
            if "images" in node_output:
                images = []
                for image_info in node_output["images"]:
                    response = requests.get(
                        f"{server_url}/view?filename={image_info['filename']}"
                        f"&subfolder={image_info['subfolder']}"
                        f"&type={image_info['type']}"
                    )
                    images.append(response.content)  # 二进制图像数据
                output_images[node_id] = images
        return output_images
        
    def comfyui_prompt_update_value(self, node_idx, input_key, new_value, comfyui_api_prompt:dict):
        # 更新工作流节点的值
        updated_api = copy.deepcopy(comfyui_api_prompt)
        if node_idx in updated_api.keys():
            updated_api[node_idx]["inputs"][input_key] = new_value
        return updated_api
    
    def read_json_file(self, json_path):
        """
        读取工作流文件
        """
        wf_loaded = None
        with open(json_path, 'r', encoding='utf-8') as f:
            wf_loaded = json.load(f)  # 正确用法：先打开文件，再传递给 json.load
        return wf_loaded
    
    def save_base64_as_png(self, base64_string, output_file_path):
        """
        将 Base64 编码的字符串保存为 PNG 图片
        
        参数:
            base64_string: Base64 编码的图片数据
            output_file_path: 输出图片文件路径
        """
        try:
            # 检查 Base64 字符串是否包含头部信息（如"data:image/png;base64,"）
            if ',' in base64_string:
                # 分割头部和实际数据
                base64_string = base64_string.split(',')[1]
            
            # 解码 Base64 字符串为二进制数据
            image_data = base64.b64decode(base64_string)
            
            # 将二进制数据写入文件
            with open(output_file_path, 'wb') as f:
                f.write(image_data)
                
            print(f"图片已成功保存到: {output_file_path}")
        except Exception as e:
            with open(f'{output_file_path}.txt', mode='w', encoding='utf-8') as f:
                f.writelines(str(base64_string))
            print(f"保存图片时出错: {str(e)}")
            print(f'图片已保存到临时文件中:  {output_file_path}.txt')

    def bytes_to_image(self, image_bytes: bytes, output_path: str = None) -> Image.Image:
        """
        将包含图片的二进制数据转换为PIL Image对象，并可选择保存到文件
        
        参数:
            image_bytes: 包含图片的二进制数据
            output_path: 可选，要保存的路径（如'/path/to/image.png'）
        
        返回:
            PIL.Image.Image对象
        """
        try:
            # 从字节数据创建图像对象
            image = Image.open(BytesIO(image_bytes))
            
            # 如果需要保存到文件
            if output_path:
                image.save(output_path)
                # print(f"图片已保存到: {output_path}")
                
            return image
            
        except Exception as e:
            print(f"转换失败: {str(e)}")
            return None

    def temp_dir_path(self):
        """获取临时目录路径。"""
        temp_dir_path = Path(__file__).resolve().parent.parent / 'temp_files' / 'comfy_imgs'
        temp_dir_path.mkdir(parents=True, exist_ok=True)
        return str(temp_dir_path)
    
    def write_temp_png_path(self, k, generated_img_output_dir = None):
        """获取临时 PNG 文件路径。"""
        if generated_img_output_dir is None:
            return str(Path(self.temp_dir_path(), f"{k}.png"))
        else:
            return str(Path(generated_img_output_dir) / f"{k}.png")
        
    def _check_upload_img(self, img:str):
        """检查上传图片路径是否合法。"""
        if Path(img).exists() and Path(img).is_file() and Path(img).suffix.lower() in ['.jpg', '.png', '.jpeg', '.bmp']:
            return True
        else:
            return False

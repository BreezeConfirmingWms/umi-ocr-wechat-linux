import base64
import sys
import os
import time
import psutil
CurrentDir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WECHAT_OCR_DIR = os.path.join("/opt/wechat/wxocr")
DEFAULT_WECHAT_DIR = os.path.join("/opt/wechat")

import wcocr
class Api:
    def __init__(self, globalArgd):
        """
        初始化接口类，不进行耗时操作
        """
        # 检查用户是否指定路径并且路径不为空
        self.wechat_ocr_dir = (globalArgd.get("wechat_ocr_dir", "") or DEFAULT_WECHAT_OCR_DIR).replace("\\", "/")
        self.wechat_dir = (globalArgd.get("wechat_dir", "") or DEFAULT_WECHAT_DIR).replace("\\", "/")

        self._last_results = None
        print(f"OCR 接口初始化完成，WeChatOCR路径: {self.wechat_ocr_dir}, WeChat目录: {self.wechat_dir}")
    def start(self,argd):
        """
        启动OCR引擎
        """

        try:
            wcocr.init(self.wechat_ocr_dir, self.wechat_dir)
            return ""
        except Exception as e:
            return f"[Error] 初始化微信OCR失败: {str(e)}"
    def stop(self):
        try:
            for proc in psutil.process_iter(['name']):
                if proc.name() == "wcocr":
                    proc.terminate()  # 尝试优雅地终止进程
                    try:
                        proc.wait(timeout=3)  # 等待进程结束，最多3秒
                    except psutil.TimeoutExpired:
                        proc.kill()  # 如果超时未结束，强制杀死
                    print(f"已终止进程：{proc.name()} (PID: {proc.pid})")
        except Exception as e:
            print(f"终止进程失败：{e}")
        print("OCR 引擎已停止。")


    def runPath(self, imgPath: str):
        """
        输入路径进行 OCR
        """
        try:
            return self._process_ocr(imgPath)
        except Exception as e:
            return {"code": 102, "data": f"[Error] 路径识别失败：{str(e)}"}

    def runBytes(self, imageBytes):
        """
        输入字节流进行 OCR
        """
        try:
            temp_path = self._save_temp_file(imageBytes, "temp_image.png")
            result = self._process_ocr(temp_path)
            os.remove(temp_path)  # 删除临时文件
            return result
        except Exception as e:
            return {"code": 102, "data": f"[Error] 字节流识别失败：{str(e)}"}

    def runBase64(self, imageBase64):
        """
        输入 Base64 字符串进行 OCR
        """
        try:
            imageBytes = base64.b64decode(imageBase64)
            return self.runBytes(imageBytes)
        except Exception as e:
            return {"code": 102, "data": f"[Error] Base64 识别失败：{str(e)}"}
    def _process_ocr(self, imgPath: str):
        """
        通用 OCR 处理逻辑
        """
        self._last_results = None  # 重置结果状态

        # 启动 OCR 任务
        start_time = time.time()
        
        
        self._last_results = wcocr.ocr(imgPath)
        # 等待任务完成，带超时机制
        timeout = 10
        if time.time() - start_time > timeout:
            raise TimeoutError("OCR 任务超时")

        if self._last_results is not None:
            return self._last_results
        else:
            return {"code": 102, "data": "[Error] 未能获取 OCR 结果"}

    def _ocr_result_callback(self, img_path: str, results: dict):
        """
        OCR 结果回调函数，将结果转换为统一格式
        """
        try:
            if "ocr_response" in results:
                ocr_data = [
                    {
                        "text": item["text"],
                        "box": [
                            [item["left"], item["top"]],
                            [item["right"], item["top"]],
                            [item["right"], item["bottom"]],
                            [item["left"], item["bottom"]],
                        ],
                        "score": item["rate"],  # 默认置信度为 1
                    }
                    for item in results["ocr_response"]
                ]
                self._last_results = {"code": 100, "data": ocr_data}
            else:
                self._last_results = {"code": 101, "data": ""}
        except Exception as e:
            self._last_results = {"code": 102, "data": f"[Error] 结果处理失败：{str(e)}"}

    @staticmethod
    def _save_temp_file(imageBytes, file_name):
        """
        将字节流保存为临时文件
        """
        temp_path = os.path.join(os.getcwd(), file_name)
        with open(temp_path, "wb") as f:
            f.write(imageBytes)
        return temp_path


def wechat_ocr(image_path):
    # wechat_path = find_wechat_path()
    # wechatocr_path = find_wechatocr_exe()
    wechat_path =  "/opt/wechat"
    wechatocr_path = "/opt/wechat/wxocr"
    if not wechat_path or not wechatocr_path:
        return []  # 返回空结果
    
    wcocr.init(wechatocr_path, wechat_path)
    result = wcocr.ocr(image_path)
    texts = []

    for temp in result['ocr_response']:
        text = temp['text']
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='ignore')
        texts.append(text)
    
    return texts
import math
import typing
import numpy as np
from PIL import Image
from io import BytesIO
from ultralytics import YOLO
import json
import cv2
from utils import ProjectPath
from utils.dom_result_handler import DOMResultHandler
import os
from os import path


class DOMInspector:
    """
    DOMInspector类用于在图像中检测DOM元素，并执行OCR识别。

    Args:
        yolo_model (str): YOLO模型的路径。

    Attributes:
        _yolo_model (str): YOLO模型的路径。
    """

    DEFAULT_NUM_PROCESSES = math.floor(os.cpu_count() / 2)
    DEFAULT_LANG = 'ch'

    def __init__(self, yolo_model: str, ocr: str = 'paddleocr'):
        """
        初始化DOMInspector类。

        Args:
            yolo_model (str): YOLO模型的路径。
        """
        self._yolo_model = yolo_model
        self._ocr = ocr


    def __call__(self,
                 image: bytes,
                 lang: str = 'ch',
                 dom_search: typing.Callable = None,
                 use_ocr: bool = True,
                 page_index: int = 0,
                 **kwargs
                 ) -> DOMResultHandler:
        """
        在图像中检测DOM元素并执行OCR识别。

        Args:
            image (bytes): 输入的图像字节数据。
            lang (str, optional): OCR识别使用的语言。默认为'ch'。
            dom_search (Callable, optional): 用于筛选DOM元素的自定义搜索函数。默认为None。

        Returns:
            DOMResultHandler: DOMResultHandler实例化对象。

        Notes:
            - 输入图像应为字节数据。
            - 如果提供了dom_search函数，则只返回满足搜索条件的DOM元素。

        Example:
                browser_launcher = BrowserLauncher(headless=True)
                browser = browser_launcher.browser
                page = browser_launcher.page
                page.goto('https://www.bilibili.com/', timeout=0)
                screenshot = page.screenshot()
                dom_inspector = DOMInspector(yolo_model=path.join(ProjectPath.root_path, 'bilibili_best.pt'))
                result = dom_inspector(image=screenshot, dom_search=lambda item: item.get('name') == 'channel-link' and '鬼畜' in item.get('text'))
                result.click()
        """
        ocr_type, ocr_model = None, None
        if use_ocr:
            ocr_type, ocr_model = self._get_ocr_model(self._ocr, lang)
        image_array = np.frombuffer(image, dtype=np.uint8)
        image_cv = cv2.imdecode(image_array, flags=cv2.IMREAD_COLOR)

        image_object = Image.open(BytesIO(image))
        self._model = YOLO(self._yolo_model)

        result = self._model(image_object)
        image_object.close()
        dom_list = []
        for index, item in enumerate(result):
            item = json.loads(item.tojson())
            if not item:
                continue
            if use_ocr:
                dom_list += [self._with_ocr((item, image_cv, dom_search, ocr_type, ocr_model)) for item in item]
            else:
                dom_list += item
        return DOMResultHandler(dom_list, page_index=page_index)

    def _with_ocr(self, d):
        dom_detail, image_cv, dom_search, ocr_type, ocr_model = d
        box: dict = dom_detail.get('box')
        name = dom_detail.get('name')
        _class = dom_detail.get('class')
        confidence = dom_detail.get('confidence')
        cropped_image = image_cv[int(box.get('y1')): int(box.get('y2')), int(box.get('x1')): int(box.get('x2'))]
        cropped_arr = np.array(cropped_image)
        if ocr_type:
            text_result = ocr_model.ocr(cropped_arr, cls=False, det=False)
            text_result = [item[0][0] for item in text_result]
        else:
            text_result = ocr_model.readtext(cropped_arr, detail=0)
        result_with_text = {"box": box, "name": name, "class": _class, "confidence": confidence,
                            "text": text_result}
        if isinstance(dom_search, typing.Callable) and dom_search(result_with_text):
            return result_with_text
        elif not dom_search:
            return result_with_text

    def _get_ocr_model(self, ocr: str, lang: str):
        from easyocr import Reader
        model_path = path.join(ProjectPath.public_path, 'easyocr_model')
        if not ocr:
            raise ValueError(f'不支持传入的ocr参数：{ocr}')
        if ocr not in ['paddleocr', 'easyocr']:
            raise ValueError(f'仅支持两种ocr模型，请传入 "paddleocr" 或是 "easyocr" ')
        if ocr == 'paddleocr':
            try:
                from paddleocr import PaddleOCR
                ocr = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)
                return 1, ocr
            except:
                print('PP飞桨OCR使用失败，将使用EasyOCR')
                return 0, Reader(['ch_sim', 'en'], model_storage_directory=model_path, download_enabled=False)
        return 0, Reader(['ch_sim', 'en'], model_storage_directory=model_path, download_enabled=False)
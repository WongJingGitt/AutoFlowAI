import math
import typing
import numpy as np
from PIL import Image
from io import BytesIO
from paddleocr import PaddleOCR
from ultralytics import YOLO
import json
import cv2
from utils.dom_result_handler import DOMResultHandler
from multiprocessing import Pool
from contextlib import contextmanager
import os


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

    def __init__(self, yolo_model: str):
        """
        初始化DOMInspector类。

        Args:
            yolo_model (str): YOLO模型的路径。
        """
        self._yolo_model = yolo_model

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
                d = [(item, image_cv, dom_search, lang) for item in item]
                with self._create_pool() as pool:
                    dom_list += list(pool.imap_unordered(self._with_ocr, d))
            else:
                dom_list += item
        return DOMResultHandler(dom_list, page_index=page_index)

    @contextmanager
    def _create_pool(self, num_processes=DEFAULT_NUM_PROCESSES) -> Pool:
        with Pool(processes=num_processes) as pool:
            yield pool

    def _with_ocr(self, d):
        dom_detail, image_cv, dom_search, lang = d
        box: dict = dom_detail.get('box')
        name = dom_detail.get('name')
        _class = dom_detail.get('class')
        confidence = dom_detail.get('confidence')
        cropped_image = image_cv[int(box.get('y1')): int(box.get('y2')), int(box.get('x1')): int(box.get('x2'))]
        cropped_arr = np.array(cropped_image)
        ocr = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False, use_gpu=False)
        text_result = ocr.ocr(cropped_arr, cls=False)
        text_result = text_result
        text_result = [item[-1][0] for item in text_result]
        result_with_text = {"box": box, "name": name, "class": _class, "confidence": confidence,
                            "text": text_result}
        if isinstance(dom_search, typing.Callable) and dom_search(result_with_text):
            return result_with_text
        elif not dom_search:
            return result_with_text

import typing
import numpy as np
from PIL import Image
from io import BytesIO
from paddleocr import PaddleOCR
from ultralytics import YOLO
import json
import cv2


class DOMInspector:
    def __init__(self, yolo_model: str):
        self._yolo_model = yolo_model
        self._result = []

    def __call__(self, image: bytes, lang: str = 'ch', dom_search: typing.Callable = None, **kwargs):
        image_array = np.frombuffer(image, dtype=np.uint8)
        image_cv = cv2.imdecode(image_array, flags=cv2.IMREAD_COLOR)

        image_object = Image.open(BytesIO(image))
        self._model = YOLO(self._yolo_model)

        result = self._model(image_object)

        image_object.close()

        ocr = PaddleOCR(use_angle_cls=True, lang=lang)
        for index, item in enumerate(result):
            item = json.loads(item.tojson())
            if len(item) <= 0:
                continue
            for dom_detail in item:
                box: dict = dom_detail.get('box')
                name = dom_detail.get('name')
                _class = dom_detail.get('class')
                confidence = dom_detail.get('confidence')
                cropped_image = image_cv[int(box.get('y1')): int(box.get('y2')), int(box.get('x1')): int(box.get('x2'))]
                cropped_arr = np.array(cropped_image)

                text_result = ocr.ocr(cropped_arr, cls=True)
                text_result = text_result[0]
                text_result = [item[1][0] for item in text_result]
                result_with_text = {"box": box, "name": name, "class": _class, "confidence": confidence,
                                    "text": text_result}
                if isinstance(dom_search, typing.Callable) and dom_search(result_with_text):
                    self._result.append(result_with_text)
                elif not dom_search:
                    self._result.append(result_with_text)

    @property
    def get(self) -> list[dict[str or list or dict]]:
        return self._result

import typing

import playwright.sync_api
from utils import BrowserLauncher


class DOMResultHandler:
    def __init__(self, result_list):
        self._result_list = result_list
        self._browser_launcher = BrowserLauncher()

    def filter(self, callback: typing.Callable):
        result = [item for item in self._result_list if callback(item)]
        return DOMResultHandler(result)

    def get_texts(self):
        return [item.get('text') for item in self._result_list]

    def click(self, callback: typing.Callable = None, page_index: int = 0):
        dom_detail: dict = self._result_list[0] if not callback else \
            [item for item in self._result_list if callback(item)][0]
        box: dict = dom_detail.get('box')
        x1, y1, x2, y2 = box.values()
        x = (x2 - x1) / 2 + x1
        y = (y2 - y1) / 2 + y1
        page: playwright.sync_api.Page = self._browser_launcher.pages[page_index]
        page.mouse.click(x=x, y=y)

    # TODO: 输入，滚动等函数待补充



import typing
import playwright.sync_api
from utils import BrowserLauncher
import logging


class DOMResultHandler:
    """
    封装了针对DOMInspector返回的DOM数据，执行一系列操作的方法。

    Attributes:
        result_list (list[dict]): DOMInspector类返回的DOM数据

    Methods:
        _get_position(callback): 根据回调筛选出目标DOM，并且获取中心坐标。
        filter(callback): 使用过滤条件返回一个新的DOMResultHandler实例，包含经过筛选的元素。
        get_texts(): 获取DOM元素的文本内容列表。
        click(callback, page_index, double): 模拟点击DOM元素。
        input(text, callback, page_index): 模拟在DOM输入元素中输入文本。
        scroll(callback, page_index, scroll_x, scroll_y): 模拟在DOM元素上滚动。

    Example:
        dom_inspector = DOMInspector(yolo_model_path)
        dom_inspector_result = dom_inspector(image_bytes)
        dom_handler = DOMResultHandler(dom_inspector_result)
        filtered_handler = dom_handler.filter(lambda item: '示例' in item.get('text'))
        texts = dom_handler.get_texts()
        dom_handler.click(callback=lambda item: 'button' in item.get('name'))
        dom_handler.input('Hello World!', callback=lambda item: 'input' in item.get('name'))
        dom_handler.scroll(callback=lambda item: 'scroll' in item.get('name'))
    """

    def __init__(self, result_list, page_index: int = 0):
        """
        初始化DOMResultHandler，传入一系列DOM元素详细信息。

        Args:
            result_list (list[dict]): 一系列DOM元素详细信息，每个元素都用字典表示。
        """
        self._logging = logging.getLogger('Handler')
        self._result_list = result_list
        self._browser_launcher = BrowserLauncher()
        self._page = self._browser_launcher.pages[page_index]
        self._page_index = page_index

    def _get_position(self, callback: typing.Callable = None) -> tuple[float, float] or None:
        """
        根据回调筛选出目标DOM，并且获取中心坐标。。

        Args:
            callback (Callable): 用于筛选DOM元素的回调函数。

        returns:
            tuple[float, float] or None: DOM元素的中心坐标 (x, y)，如果找不到则返回None。
        """
        dom_detail: list[dict] = self._result_list if not callback else \
            [item for item in self._result_list if callback(item)]
        if not dom_detail:
            self._logging.setLevel(logging.INFO)
            self._logging.info('没有捕获得到元素！')
            return None, None
        dom_detail: dict = dom_detail[0]
        box: dict = dom_detail.get('box')
        x1, y1, x2, y2 = box.values()
        x = (x2 - x1) / 2 + x1
        y = (y2 - y1) / 2 + y1
        return x, y

    def filter(self, callback: typing.Callable):
        """
         根据回调返回一个新的DOMResultHandler实例，包含经过筛选的元素。

         Args:
             callback (Callable): 用于筛选DOM元素的回调函数。

         returns:
             DOMResultHandler: 包含筛选元素的新DOMResultHandler实例。
         """
        result = [item for item in self._result_list if callback(item)]
        return DOMResultHandler(result, page_index=self._page_index)

    @property
    def get_texts(self):
        """
        获取DOM元素的文本内容列表。

        returns:
            list[str]: 包含DOM元素文本内容的列表。
        """
        return [item.get('text') for item in self._result_list]

    def click(self, callback: typing.Callable = None, page_index: int = None, double: bool = False):
        """
        点击DOM元素。

        Args:
            callback (Callable): 用于筛选DOM元素的回调函数。
            page_index (int): 执行点击操作的页面索引。
            double (bool): 是否执行双击操作。

        returns:
            None
        """
        x, y = self._get_position(callback=callback)
        if not x or not y:
            return None
        page_index = self._page_index if not page_index else page_index
        page: playwright.sync_api.Page = self._browser_launcher.pages[page_index]
        if not double:
            page.mouse.click(x=x, y=y)
        elif double:
            page.mouse.dblclick(x=x, y=y)

    def input(self, text: str, clear: bool = True, callback: typing.Callable = None, page_index: int = None):
        """
        模拟在DOM输入元素中输入文本。

        Args:
            text (str): 需要输入的文本。
            clear (bool): 是否需要在输入之前清空文本框，默认Ture 清除。
            callback (Callable): 用于筛选DOM元素的回调函数。
            page_index (int): 执行输入操作的页面索引。

        returns:
            None
        """
        x, y = self._get_position(callback=callback)
        if not x or not y:
            return None
        page_index = self._page_index if not page_index else page_index
        page: playwright.sync_api.Page = self._browser_launcher.pages[page_index]
        page.mouse.click(x=x, y=y)
        if clear:
            page.keyboard.press('Control+A')
            page.keyboard.press('Backspace')
        page.keyboard.insert_text(text=text)

    def scroll(self, callback: typing.Callable = None, page_index: int = None, scroll_x: float = 100.00,
               scroll_y: float = 100.00):
        """
        模拟在DOM元素上滚动。

        Args:
            callback (Callable): 用于筛选DOM元素的回调函数。
            page_index (int): 执行滚动操作的页面索引。
            scroll_x (float): 水平方向的滚动量。
            scroll_y (float): 垂直方向的滚动量。

        returns:
            None
        """
        x, y = self._get_position(callback=callback)
        page_index = self._page_index if not page_index else page_index
        page: playwright.sync_api.Page = self._browser_launcher.pages[page_index]
        page.mouse.move(x, y)
        page.wait_for_timeout(500)
        page.mouse.wheel(delta_x=scroll_x, delta_y=scroll_y)
        page.wait_for_timeout(500)

    @property
    def get(self) -> list:
        """
        returns:
            输入的原始数据
        """
        return self._result_list

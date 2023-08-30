import playwright.sync_api
from playwright.sync_api import sync_playwright, expect


class Browser:
    """
    基于playwright封装了启动类，可以快速启动指定的浏览器，并且获取浏览器对象与页面对象
    """

    BROWSER_MAP = {
        'chrome': 'chromium',
        'firefox': 'firefox',
        'webkit': 'webkit'
    }
    DEFAULT_VIEWPORT_SIZE = {'width': 1920, 'height': 1080}

    def __init__(self, browser_type: str = 'chrome', headless: bool = False, playwright_: tuple or bool = False):
        """
        构造函数
        :param browser_type: 需要启动的浏览器，可选 chromium、firefox、webkit，默认chrome
        :param headless: 是否以无头模式启动，默认False
        """
        if not playwright_:
            self._playwright = sync_playwright().start()
            self._page, self._browser = self._launcher(browser_type or 'chrome', headless)
        else:
            self._page, self._browser = playwright_
        self._browser.on('page', lambda page: page.set_viewport_size(self.DEFAULT_VIEWPORT_SIZE))
        # TODO: 新窗口打开时视图分辨率没有生效，待优化

    def __del__(self):
        try:
            self._browser.close()
            self._playwright.stop()
        except TypeError:
            pass

    def _launcher(self, browser_type: str or None = None, headless: bool = False) -> (
            playwright.sync_api.Page, playwright.sync_api.BrowserContext):
        """
        浏览器启动的私有函数，在构造函数内被调用。
        :param browser_type: 需要启动的浏览器，可选 chromium、firefox、webkit，默认chrome
        :param headless: 是否以无头模式启动，默认False
        :return: 由页面对象与浏览器对象组成的元组
        """
        browser_name = self.BROWSER_MAP.get(browser_type, None)
        if not browser_name:
            raise ValueError(f'传入的浏览器: {browser_type} 不存在. 支持的浏览器: chromium, firefox, webkit')

        browser_type = browser_type if browser_type == 'chrome' else None

        _browser = getattr(self._playwright, browser_name).launch(headless=headless, channel=browser_type)
        _browser = _browser.new_context()
        _page = _browser.new_page()
        _page.set_viewport_size(self.DEFAULT_VIEWPORT_SIZE)
        return _page, _browser

    def get_element(self, selector: str, selector_type: str = None, element_page: playwright.sync_api.Page = None,
                    has_text: str = None) -> playwright.sync_api.Locator:
        """
        基于playwright.locator封装用于捕获页面元素的方法。
        :param (str) selector: 元素字符串。
        :param (str) selector_type: 可选。元素类型，默认None
        :param (Page) element_page: 可选。元素所在的页面对象，默认为初始页面
        :param (str) has_text: 可选。目标元素包含的文本，用于辅助捕获元素。默认None
        :return: Locator

        例：

        ```python
            input_elem = browser_launcher.get_element(selector='sb_form_q', selector_type='id')
            input_elem = browser_launcher.get_element(selector='#sb_form_q', selector_type='css')
            input_elem = browser_launcher.get_element(selector='button[class="tea-btn tea-btn--weak"]', selector_type='css', has_text='Revenue')
        ```
        """
        element_page = self.page if element_page is None else element_page
        if selector_type:
            selector_type = selector_type.lower()
            type_list = ['css', 'id', 'class', 'class_name', 'name', 'text', 'link_text', 'tag_name', 'xpath']

            if selector_type not in type_list:
                raise TypeError(f'传入的元素类型："{selector_type}" 不存在，支持的定位类型：{type_list}')

            return element_page.locator(selector=f'{selector_type}={selector}', has_text=has_text)

        else:
            return element_page.locator(selector=selector, has_text=has_text)

    def type(self, selector, text: str = '', selector_type: str = None, clear: bool = True,
             delay: float | int = 0 or 0.00,
             element_page=None):
        """
        基于playwright中type封装的一个文本输入方法，可以实现一次输入多个文本框，清空文本框等功能
        :param (str|list|Locator) selector: 文本框的元素，可以是元素的字符串，或者元素对象。也可以是由元素和元素对象组成的list
        :param (str) text: 需要输入的文本
        :param (str) selector_type: 可选。当传入是字符串元素时指定元素类型
        :param (bool) clear: 可选。是否在每次输入前清空文本框，默认清除
        :param (int | float) delay: 可选。每个字符输入的时间间隔，单位秒。默认 0
        :param (Page) element_page: 可选。需要输入的页面，默认首次打开的页面。
        :return: self，实现链式调用

        例：
        ```python
                input_elem = browser_launcher.get_element(selector='sb_form_q', selector_type='id')

                elements = [
                    {"selector": 'sb_form_q', "selector_type": 'id', 'text': '全量参数测试、'},
                    {"selector": '#sb_form_q', 'text': '带了text、'},
                    {"selector": 'id=sb_form_q'},
                    {"selector": input_elem, 'text': '这是元素对象输入测试、'}
                ]

                browser_launcher.type(selector=elements, text='这是默认的text、', clear=False)

                browser_launcher.type(selector='sb_form_q', selector_type='id', text='这是单独输入测试', clear=False)

                browser_launcher.page_assert(input_elem).to_have_value(
                    '全量参数测试、带了text、这是默认的text、这是元素对象输入测试、这是单独输入测试')
        ```

        """
        element_page = self._page if not element_page else element_page

        if isinstance(selector, str):
            typer = self.get_element(selector=selector, selector_type=selector_type, element_page=element_page)
            if clear: typer.clear()
            typer.type(text, delay=delay * 1000)
        elif isinstance(selector, playwright.sync_api.Locator):
            if clear: selector.clear()
            selector.type(text, delay=delay * 1000)
        elif isinstance(selector, list):
            for element_text in selector:
                element = element_text.get('selector')
                _text = element_text.get('text', text)
                _selector_type = element_text.get('selector_type', selector_type)
                _delay = element_text.get('delay', delay)
                if isinstance(element, playwright.sync_api.Locator):
                    if clear: element.clear()
                    element.type(_text, delay=_delay * 1000)
                    continue
                typer = self.get_element(selector=element, selector_type=_selector_type, element_page=element_page)
                if clear: typer.clear()
                typer.type(_text, delay=_delay * 1000)

        return self

    def click(self, selector, selector_type=None, delay=0, element_page=None, has_text=None):
        """
        基于playwright封装的点击方法，可以对多个元素进行过批量点击
        :param (str|list|Locator) selector: 需要点击的元素元素，可以是元素的字符串，或者元素对象。也可以是由元素和元素对象组成的list
        :param (str) selector_type: 可选。当传入是字符串元素时指定元素类型，list字典内支持单独传入作为单次点击的参数
        :param (int) delay: 可选。批量点击时每次点击相隔的时间，list字典内支持单独传入作为单次点击的参数
        :param (Page) element_page: 可选。需要点击元素所处的页面对象，默认为最开始的默认页面。
        :param (str) has_text: 可选。点击元素包含的文本，用于辅助捕获元素，list字典内支持单独传入作为单次点击的参数
        :return: self，用做链式调用。

        例：

        ```python
            browser_launcher.click(
                selector=[
                    {'selector': 'button[class="tea-btn tea-btn--weak"]', 'has_text': 'Revenue', 'selector_type': 'css'},
                    {'selector': 'button[class="tea-btn tea-btn--weak"]', 'has_text': 'D2(T-1)', 'selector_type': 'css'},
                    {'selector': 'button[class="tea-btn tea-btn--weak"]', 'has_text': 'New Users', 'selector_type': 'css'},
                    {'selector': 'button[class="tea-btn tea-btn--weak"]', 'has_text': 'ARPU($)', 'selector_type': 'css'}
                ],
                delay=2
            )
        ```
        """
        element_page = self._page if not element_page else element_page
        if isinstance(selector, str):
            element = self.get_element(selector, selector_type, element_page, has_text=has_text)
            element_page.wait_for_timeout(delay * 1000)
            element.click()
        elif isinstance(selector, playwright.sync_api.Locator):
            element_page.wait_for_timeout(delay * 1000)
            selector.click()
        elif isinstance(selector, list):
            for element_dict in selector:
                elem = element_dict.get('selector')
                delay_ = element_dict.get('delay', delay)
                has_text_ = element_dict.get('has_text', has_text)
                selector_type_ = element_dict.get('selector_type', selector_type)
                if not isinstance(element_dict, dict): raise TypeError(f'list中的元素 "{element_dict}" 不是字典')
                if not elem: raise KeyError('元素字典中 selector 不存在')
                if isinstance(elem, playwright.sync_api.Locator):
                    element_page.wait_for_timeout(delay_ * 1000)
                    elem.click()
                    continue
                element_page.wait_for_timeout(delay_ * 1000)
                self.get_element(selector=elem, has_text=has_text_, selector_type=selector_type_,
                                 element_page=element_page).click()
        return self

    def page_assert(self,
                    page_or_locator: playwright.sync_api.Page | playwright.sync_api.Locator) -> playwright.sync_api.expect:
        """
        页面断言方法
        :param page_or_locator: 页面对象或选择器
        :return: expect
        """
        return expect(page_or_locator)

    @property
    def page(self) -> playwright.sync_api.Page:
        """
        获取默认的页面对象
        :return: 默认打开的页面对象
        """
        return self._page

    @property
    def browser(self) -> playwright.sync_api.BrowserContext:
        """
        获取浏览器对象
        :return: 浏览器对象
        """
        return self._browser

    @property
    def new_page(self) -> playwright.sync_api.Page:
        """
        打开有一个新的页面
        :return: Page
        """
        new_page = self._browser.new_page()
        new_page.set_viewport_size(self.DEFAULT_VIEWPORT_SIZE)
        return new_page

    @property
    def pages(self) -> list[page]:
        return self.browser.pages


class BrowserLauncher:
    _instance = None

    def __new__(cls, browser_type: str = 'chrome', headless: bool = False, playwright_: tuple or bool = False,
                **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance = Browser(browser_type=browser_type, headless=headless, playwright_=playwright_)
        return cls._instance

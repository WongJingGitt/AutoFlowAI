import math
import os
import random
import typing
from datetime import datetime
from os import path
from playwright.sync_api import Locator, ElementHandle
import yaml
from utils.browser_launcher import BrowserLauncher
from utils.project_path import ProjectPath
import shutil

REDIRECT_TIME = 10000


class LabelGenerator:
    """
    从网页中生成带标签的数据，用于目标检测任务。
    """

    def __init__(self, url, before_start: typing.Callable = None, sources_dir_name: str or bool = None,
                 datasets_classify: bool = True):
        """
        初始化LabelGenerator对象。

        :param url: 要访问的初始URL。
        :param before_start: 在开始之前要执行的回调函数，可选填。
        :param sources_dir_name: 数据存储目录的名称，仅传入文件夹名称，不是绝对路径！不是绝对路径！不是绝对路径！。可选填，默认当前的时间，例如：2023_08_20_04_44_33
        :param datasets_classify: 是否自动分类训练集与验证集，默认开启。
        """
        browser_launcher = BrowserLauncher()
        self.__page = browser_launcher.page
        self.__page.goto(url)

        if before_start:
            before_start(browser_launcher)
            self.__page.wait_for_timeout(3000)

        # 路径处理
        self._parent_path = path.join(ProjectPath.datasets_path,
                                      sources_dir_name if sources_dir_name else datetime.now().strftime(
                                          '%Y_%m_%d_%H_%M_%S'))
        self._image_path = path.join(self._parent_path, "images")
        self._label_path = path.join(self._parent_path, "labels")
        if not path.exists(self._parent_path): os.mkdir(self._parent_path)
        if not path.exists(self._image_path): os.mkdir(self._image_path)
        if not path.exists(self._label_path): os.mkdir(self._label_path)
        if not path.exists(path.join(self._image_path, 'train')): os.mkdir(path.join(self._image_path, 'train'))
        if not path.exists(path.join(self._label_path, 'train')): os.mkdir(path.join(self._label_path, 'train'))
        if not path.exists(path.join(self._image_path, 'val')): os.mkdir(path.join(self._image_path, 'val'))
        if not path.exists(path.join(self._label_path, 'val')): os.mkdir(path.join(self._label_path, 'val'))

        config_path = path.join(ProjectPath.config_path, 'label_generator.yaml')

        with open(config_path, 'r', encoding='utf-8') as f:
            config_data: dict = yaml.safe_load(f)
            f.close()
        self._selectors = config_data.get('selectors')
        urls = config_data.get('pages')

        with open(path.join(self._parent_path, 'class.txt'), 'w', encoding='utf-8') as fw:
            fw.write('\n'.join(self._selectors))
            fw.close()

        self._filelist = []

        print('开始寻找DOM元素')
        print()

        for url in urls:
            self.__page.goto(url)
            self.__page.wait_for_timeout(REDIRECT_TIME)

            visible, hidden = self._element_visibility_classify(selector_strs=self._selectors)

            # 首先搜一遍初始的位置，然后把hidden(当前处于可视窗口外)中还没有进行捕获的元素逐一地进行滚动到可视窗口内进行捕获，然后更新hidden直到hidden为空。
            while True:
                data_name = f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}__{int(random.random() * 10000000)}"
                yolo_datas = [f'{index} {self._element_position_for_yolo(selector)}' for index, selector in visible]

                # 爬B站首页时出现空yolo_datas陷入死循环的情况，优化这类场景
                if len(yolo_datas) <= 0:
                    print(url, '搜寻完毕')
                    print()
                    break

                with open(path.join(self._label_path, f'{data_name}.txt'), 'w') as fw:
                    yolo_datas = '\n'.join(yolo_datas)
                    self.__page.screenshot(path=path.join(self._image_path, f'{data_name}.png'))
                    self._filelist.append(data_name)
                    fw.write(yolo_datas)
                    fw.close()

                print(data_name, '已写入')
                print()

                if len(hidden) <= 0:
                    print(url, '搜寻完毕')
                    print()
                    break
                hidden[0][1].scroll_into_view_if_needed()

                visible, hidden = self._element_visibility_classify(selector_strs=hidden)

        if datasets_classify: self._datasets_classify()

        with open(path.join(ProjectPath.yamls_path, f'{sources_dir_name}.yaml'), 'w') as yw:
            yaml.dump({
                "path": self._parent_path,
                "train": "images/train",
                "val": "images/val",
                "nc": len(self._selectors),
                "names": self._selectors
            }, yw)
            yw.close()

    def _visible_check(self, element: Locator or ElementHandle) -> bool:
        """
        检查给定的DOM元素是否在视口内可见，避免截图时目标Dom处于窗口外，但是却处于已加载的Dom树内。

        :param element: 要检查的DOM元素。
        :return: 如果元素在视口内可见，则为True，否则为False。
        """
        rect = element.bounding_box()
        viewport_width = self.__page.viewport_size['width']
        viewport_height = self.__page.viewport_size['height']
        return (0 <= rect['x'] < viewport_width and
                0 <= rect['y'] < viewport_height and
                0 <= rect['x'] + rect['width'] <= viewport_width and
                0 <= rect['y'] + rect['height'] <= viewport_height and
                element.is_visible())

    def _element_visibility_classify(self, selector_strs: list[str or Locator or ElementHandle]) -> tuple[
        list[Locator or ElementHandle], list[Locator or ElementHandle]]:
        """
        根据元素在窗口内的可见性，将DOM元素分类为窗口内可见、窗口内不可见或隐藏。

        :param selector_strs: 要分类的选择器列表。
        :return: 包含可见和隐藏元素的元组。
        """
        visible = []
        hidden = []

        for index, selector_str in enumerate(selector_strs):
            # 判断是否是初次调用，初次调用时selector_str的是字符串。
            if isinstance(selector_str, str):
                selector_str = self._convert_selector(selector_str)
                selectors = self.__page.query_selector_all(selector_str)
                # 优化处理，确保selectors是可迭代对象
                selectors = selectors if len(selectors) > 0 else []
            else:
                # 优化处理，当不是初次调用时传入的格式时 (label索引, 元素对象)。如果不用数组包裹后续遍历会遍历元组导致_, selector = result分解失败
                selectors = [selector_str]

            for selector in selectors:
                # 如果是初次调用，把label索引和元素对象用元组绑定
                result = selector if not isinstance(selector_str, str) else (index, selector)
                _, selector = result
                try:
                    if self._visible_check(selector):
                        visible.append(result)
                    elif not self._visible_check(selector):
                        hidden.append(result)
                except TypeError:
                    pass

        return visible, hidden

    def _element_position_for_yolo(self, element: Locator or ElementHandle) -> str:
        """
        将DOM元素的位置和尺寸转换为YOLO格式的标签，当元素处于窗口外时，滚动事件在这里被触发。

        :param element: 要转换的DOM元素。
        :return: YOLO格式的标签字符串。
        """
        rect = element.bounding_box()
        viewport_width = self.__page.viewport_size['width']
        viewport_height = self.__page.viewport_size['height']

        center_x = (rect['x'] + rect['width'] / 2) / viewport_width
        center_y = (rect['y'] + rect['height'] / 2) / viewport_height

        width = rect['width'] / viewport_width
        height = rect['height'] / viewport_height

        return f"{center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}"

    def _convert_selector(self, selector_str: str) -> str:
        """
        将选择器字符串转换为有效的CSS选择器。

        :param selector_str: 要转换的选择器字符串。
        :return: 转换后的CSS选择器字符串。
        """
        selector_str = f'.{selector_str.replace(" ", ".")}' if ' ' in selector_str else selector_str
        selector_str = f'.{selector_str}' if '.' not in selector_str and '#' not in selector_str else selector_str
        return selector_str

    def _datasets_classify(self):
        val_count = math.floor(len(self._filelist) / 15)
        val_list = random.choices(self._filelist, k=val_count)
        train_list = [filename for filename in self._filelist if filename not in val_list]
        for filename in val_list:
            image_path = path.join(self._image_path, f'{filename}.png')
            new_path = path.join(self._image_path, f'val/{filename}.png')
            shutil.move(image_path, new_path)
            label_path = path.join(self._label_path, f'{filename}.txt')
            new_path = path.join(self._label_path, f'val/{filename}.txt')
            shutil.move(label_path, new_path)

        for filename in train_list:
            image_path = path.join(self._image_path, f'{filename}.png')
            new_path = path.join(self._image_path, f'train/{filename}.png')
            shutil.move(image_path, new_path)
            label_path = path.join(self._label_path, f'{filename}.txt')
            new_path = path.join(self._label_path, f'train/{filename}.txt')
            shutil.move(label_path, new_path)


if __name__ == '__main__':
    with open(path.join(ProjectPath.config_path, 'bilibili_info.yaml'), 'r') as rf:
        user_info = yaml.safe_load(rf)


    def before(launcher: BrowserLauncher):
        launcher.page.locator('.v-popover-wrap', has_text='登录').click()
        launcher.page.wait_for_selector(selector="input[placeholder='请输入账号']", timeout=0)
        launcher.type(selector=[
            {"selector": "input[placeholder='请输入账号']", "selector_type": "css", "text": user_info.get('username')},
            {"selector": "input[placeholder='请输入密码']", "selector_type": "css", "text": user_info.get('password')}
        ], delay=0.5)
        launcher.click('.btn_primary ', selector_type='css', has_text='登录')
        launcher.page.wait_for_timeout(10000)


    lg = LabelGenerator('https://www.bilibili.com/', before_start=before,
                        sources_dir_name='bilibili')

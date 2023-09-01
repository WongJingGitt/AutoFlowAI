import time
from os import path
from utils import BrowserLauncher, DOMInspector, ProjectPath

if __name__ == '__main__':
    browser_launcher = BrowserLauncher(headless=False)
    browser = browser_launcher.browser
    page = browser_launcher.page
    page.goto('https://www.bilibili.com/', timeout=0)

    screenshot = page.screenshot()

    dom_inspector = DOMInspector(yolo_model=path.join(ProjectPath.root_path, 'bilibili_best.pt'))
    result = dom_inspector(image=screenshot)

    # 点击元素
    result.click(lambda item: item.get('name') == 'channel-link' and '鬼畜' in item.get('text'))

    # 输入元素
    result.filter(lambda item: item.get('name') == 'center-search-container').input('UI自动化')

    page.keyboard.press('Enter')
    time.sleep(1)
    time.sleep(15)
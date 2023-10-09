import time
from os import path
from utils import BrowserLauncher, DOMInspector, ProjectPath

if __name__ == '__main__':
    browser_launcher = BrowserLauncher(headless=False)
    browser = browser_launcher.browser
    page = browser_launcher.page
    page.goto('https://search.bilibili.com/all?keyword=UI%E8%87%AA%E5%8A%A8%E5%8C%96', timeout=0)

    screenshot = page.screenshot()
    dom_inspector = DOMInspector(yolo_model=path.join(ProjectPath.root_path, 'bilibili_best.pt'))
    result = dom_inspector(image=screenshot, use_ocr=True)

    # 点击元素
    result.click(lambda item: item.get('name') == 'channel-link' and '鬼畜' in item.get('text'))

    # 输入元素
    result.filter(lambda item: item.get('name') == 'center-search-container').input('UI自动化')

    page.keyboard.press('Enter')

    page.wait_for_timeout(500)

    new_page = browser_launcher.pages[-1]

    new_screenshot = new_page.screenshot()
    new_result = dom_inspector(image=new_screenshot, use_ocr=False, page_index=-1)

    new_result.filter(lambda item: item.get('name') == 'center-search-container').input('接口自动化')

    new_page.keyboard.press('Enter')

    time.sleep(1)
    time.sleep(15)


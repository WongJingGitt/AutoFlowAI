import datetime
import time
from os import path
from utils import BrowserLauncher, DOMInspector, ProjectPath
from utils.dom_result_handler import DOMResultHandler

if __name__ == '__main__':
    browser_launcher = BrowserLauncher(headless=False)
    browser = browser_launcher.browser
    page = browser_launcher.page
    page.goto('https://www.bilibili.com/', timeout=0)

    screenshot = page.screenshot()

    dom_inspector = DOMInspector(yolo_model=path.join(ProjectPath.root_path, 'bilibili_best.pt'))
    start_time = datetime.datetime.now()
    result = dom_inspector(image=screenshot)
    handler = DOMResultHandler(result)
    handler.click(lambda item: item.get('name') == 'channel-link' and '鬼畜' in item.get('text'))
    time.sleep(15)
from os import path
from utils import BrowserLauncher, DOMInspector, ProjectPath

if __name__ == '__main__':
    browser_launcher = BrowserLauncher(headless=True)
    browser = browser_launcher.browser
    page = browser_launcher.page
    page.goto('https://www.bilibili.com/', timeout=0)

    screenshot = page.screenshot()
    dom_inspector = DOMInspector(yolo_model=path.join(ProjectPath.root_path, 'bilibili_best.pt'))
    dom_inspector(image=screenshot, dom_search=lambda item: item.get('name') == 'channel-link' and '鬼畜' in item.get('text'))
    print(dom_inspector.get)
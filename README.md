# Auto Flow AI  
***  
Auto Flow AI是一个创新性的UI自动化框架，将计算机视觉技术与自动化操作紧密结合，旨在为开发人员和测试人员提供高效、准确且强大的界面自动化解决方案。  

## 主要特点  
  
****  

* **Yolo v8 与 OCR 整合：**  项目集成了Yolo v8目标检测算法和OCR（光学字符识别）技术，让系统能够智能地识别和定位应用界面中的各种DOM元素，同时获取DOM元素中的文本内容。  
* **智能模拟用户行为：** 利用训练有素的Yolo模型和OCR技术，Auto Flow AI可以高度模拟真实用户的操作行为，从点击到输入，甚至是文本识别和验证。这使得UI测试和操作变得更加准确和全面。  
* **自动生成训练数据集：** 项目附带专用的DOM元素数据集制作脚本，只需简单配置，系统就能自动收集DOM元素并生成训练数据集，极大地简化了模型训练的流程。  
* **稳定性与适应性：**  与传统的UI自动化方法不同，Auto Flow AI不会因为DOM元素的轻微变化而导致用例失败。其结合了先进的计算机视觉和OCR技术，可以在各种情况下保持稳定性和可靠性。  

<h2 id="quickstart">快速开始</h2>  
<hr/>

<h3 id="quickstart-step1">步骤1：安装依赖</h3>  
确保你的系统已安装以下依赖： 
  
- Python 3.10.5+  
  
> **注意：** 项目的编写与测试均在Python版本`3.10.5`下进行，在低于`3.10.5`的Python版本上可能存在兼容性问题。建议在`3.10.5`或更高版本的Python中使用。  

<h3 id="quickstart-step2">步骤2：克隆项目</h3>  
使用以下命令从Gitee克隆项目：  

```commandline
git clone https://gitee.com/wangyingjie1003/auto-flow-ai.git
cd auto-flow-ai
```
  
<h3 id="quickstart-step3">步骤3：安装项目依赖</h3>  
运行以下命令安装项目所需的依赖：  

```commandline
pip install -r requirements.txt
```  

<h3 id="quickstart-step4">步骤4：填写数据收集配置文件</h3>  
在此步骤中，你需要编辑 `config/label_generator.yaml` 文件（以下简称：配置文件），以配置数据收集的相关设置。 
  
配置文件最外层包含两个关键字：  
* **selectors：**  这是需要收集的DOM组件选择器。你可以使用 `class`、`id`、`CSS选择器`等方式。推荐使用组件的 `class` 作为选择器。一旦页面中出现带有该组件的 class，系统将自动收集数据并截图。这里有两种支持的形式：  
  - **字符串形式：** 直接写入选择器  
    ```yaml
    selectors:
        - btn
        - input
    ```
  - **列表形式：**  写入包含 `class` 和 `name` 两个键的字典，其中 `class` 代表组件的选择器，`name` 则是组件的名称。后续识别结果中的 `name` 将使用此名称。 **注意：`name`不可以使用中文！**  
    ```yaml
    selectors:
        - class:
              btn
          name:
              default button
        - class:
              input
          name:
              default input
      ```
  > **注意：** 字符串形式，识别的结果中的`name`将直接使用选择器  
* **pages：**  在这一步，你需要写入页面的链接。脚本会遍历 `pages` 中的所有链接，并在每次打开页面时搜索 selectors 中的元素。如果找到相应的元素，则会进行记录。  
  > **提示：** 为了获得更准确的数据和训练效果，建议在这里写入不同场景的链接。多样化的页面和元素组合将有助于模型更好地适应不同的情况，提高自动化流程的稳定性和准确性。  

  这个过程中，脚本会自动滚动至元素的位置，以确保即使元素在页面底部或不可见区域，也能被正确识别和记录。  

以下是两个场景的完整示例： 

* **字符串：**  

  ```yaml
  selectors:
    - v-popover-wrap
    - channel-link
    - channel-items__right
    - center-search-container
    - bili-live-card is-rcmd
  pages:
    - https://www.bilibili.com/
    - https://www.bilibili.com/
    - https://www.bilibili.com/
    - https://www.bilibili.com/
    - https://www.bilibili.com/video/BV1LF411o7Gj
    - https://www.bilibili.com/video/BV1B4411w79q
    - https://www.bilibili.com/video/BV1884y1f7Cp
    - https://www.bilibili.com/video/BV1w44y1w7Z9
  ```  
  
* **列表：**  

  ```yaml
  selectors:
    - class:
        v-popover-wrap
      name:
        popover
    - class:
        channel-link
      name:
        channel
    - class:
        channel-items__right
      name:
        channel right
    - class:
        center-search-container
      name:
        search

  pages:
    - https://www.bilibili.com/
    - https://www.bilibili.com/
    - https://www.bilibili.com/
    - https://www.bilibili.com/
    - https://www.bilibili.com/video/BV1LF411o7Gj
    - https://www.bilibili.com/video/BV1B4411w79q
    - https://www.bilibili.com/video/BV1884y1f7Cp
    - https://www.bilibili.com/video/BV1w44y1w7Z9
    - https://www.bilibili.com/video/BV1Hx4y1X7Y9
    ```

> **注意：** 由于篇幅原因只写了部分配置数据，实际使用中请务必在pages中覆盖大量不同的场景。

<h3 id="quickstart-step5">步骤5：收集训练数据</h3>  
在这一步，将使用 utils 中的 LabelGenerator 类来收集训练数据。这个过程需要传递以下4个参数：   

* **url：** 浏览器启动时的初始页面，通常是登录页面等。
* **before_start：** 这是一个回调函数，在执行脚本之前会调用。你可以在这里执行一些前置工作，例如登录。回调函数的第一个参数是 `Browser` 类的实例化对象。  
* **sources_dir_name：**  用于在 `datasets` 文件夹下创建一个以该参数为名称的文件夹，用于存放收集到的数据集。如果不传递该参数，系统将使用当前时间作为文件夹名称。  
* **datasets_classify：** 这个参数控制在数据收集完成后是否自动划分训练集和验证集。默认值为 `True` 。如果设置为 `False` ，则需要手动划分。  

以下是一个示例代码，展示了如何使用 LabelGenerator 类：  

```python
from utils import LabelGenerator

def before(launcher):
    launcher.page.locator('.v-popover-wrap', has_text='登录').click()
    launcher.page.wait_for_selector(selector="input[placeholder='请输入账号']", timeout=0)
    launcher.type(selector=[
        {"selector": "input[placeholder='请输入账号']", "selector_type": "css", "text": 'your username'},
        {"selector": "input[placeholder='请输入密码']", "selector_type": "css", "text": 'your password'}
    ], delay=0.5)
    launcher.click('.btn_primary ', selector_type='css', has_text='登录')
    launcher.page.wait_for_timeout(10000)
    
LabelGenerator(
    url='https://www.bilibili.com',
    before_start=before,
    sources_dir_name='bilibili',
    datasets_classify=True
)
```  

在完成数据收集后，将在 `datasets` 文件夹下生成训练数据，并在 `yamls` 文件夹下使用传入的 `sources_dir_name` 参数为名称生成数据集的 YOLO 配置文件。   

这个步骤将为模型训练提供所需的数据集，并准备好后续的训练过程。  

<h3 id="quickstart-step6">步骤6：训练检测模型</h3>  

这一步，将开始训练检测模型，确保你按照推荐的配置进行操作。以下是具体的配置和步骤：  

**训练配置**  

请查阅[ultralytics官方仓库](https://github.com/ultralytics/ultralytics)，以获取与训练相关的详细配置。在这里，推荐填写以下三个配置项：  
 
* **data：** 这是数据集的配置文件，由 `LabelGenerator` 生成，存放在 `yamls` 文件夹下。  
* **model：** 选择需要训练的模型类型。可以查阅官方仓库了解更多关于不同模型的功能和类型。推荐使用 `yolov8m+`。关于模型的训练有以下两种场景：    
  - **首次训练：** 直接传模型配置文件，例如：yolov8m.yaml
  - **基于已有模型继续训练：** 传入模型路径，例如：bilibili_best.yaml
* **epochs：** 设置训练的最大轮次。在实际训练中，如果超过50轮模型没有显著提升，训练将自动终止。    

> **注意：**   
> 训练过程需要基于显卡和CUDA。你可以查阅相关教程来进行CUDA的配置和安装。  
> 
> 关于模型的选择，例如，我在测试中使用了显卡3060TI 8G，能够在 `yolov8m` 模型上进行训练。如果你拥有更强大的显卡，可以选择更大的模型以提高模型的精确度。  
> 
> 训练完成后，模型的 `.pt` 文件将保存在 `runs` 目录下。其中，`best.pt`、`last.pt`两个模型，分别代表效果最好的模型与最后一次保存的模型

**示例命令**  

以下是两种模型训练场景的示例命令：  

* **首次训练：**  

  ```commandline
  yolo detect train data=yamls/bilibili.yaml model=yolov8m.yaml epochs=1000
  ```  

* **基于已有的模型训练：**  

  ```commandline
  yolo detect train data=yamls/bilibili.yaml model=bilibili_best.pt epochs=1000
  ```

可以根据你的项目和需求，调整命令中的路径和参数。  
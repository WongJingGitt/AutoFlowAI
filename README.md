# Auto Flow AI  
***  
Auto Flow AI是一个创新性的UI自动化框架，将计算机视觉技术与自动化操作紧密结合，旨在为开发人员和测试人员提供高效、准确且强大的界面自动化解决方案。  

## 主要特点  
***  
* **Yolo v8 与 OCR 整合：**  项目集成了Yolo v8目标检测算法和OCR（光学字符识别）技术，让系统能够智能地识别和定位应用界面中的各种DOM元素，同时获取DOM元素中的文本内容。  
* **智能模拟用户行为：** 利用训练有素的Yolo模型和OCR技术，Auto Flow AI可以高度模拟真实用户的操作行为，从点击到输入，甚至是文本识别和验证。这使得UI测试和操作变得更加准确和全面。  
* **自动生成训练数据集：** 项目附带专用的DOM元素数据集制作脚本，只需简单配置，系统就能自动收集DOM元素并生成训练数据集，极大地简化了模型训练的流程。  
* **稳定性与适应性：**  与传统的UI自动化方法不同，Auto Flow AI不会因为DOM元素的轻微变化而导致用例失败。其结合了先进的计算机视觉和OCR技术，可以在各种情况下保持稳定性和可靠性。  

<h2 id="quickstart">快速开始</h2>
***  

<h3 id="quickstart-step1">步骤1：安装依赖</h3>  
确保你的系统已安装以下依赖：  
* Python 3.10.5+  
  
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
  > **注意：** str形式下，识别的结果name将直接使用选择器  
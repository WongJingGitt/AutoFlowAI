from transformers import AutoTokenizer, AutoModel


class NLP2Code:

    def __init__(self, device: str = 'cuda'):
        self._tokenizer = AutoTokenizer.from_pretrained("THUDM/codegeex2-6b", trust_remote_code=True)
        self._model = AutoModel.from_pretrained("THUDM/codegeex2-6b", trust_remote_code=True,
                                                device=device)
        self._model = self._model.eval()

    def __call__(self, message: str, language: str = 'Python', *args, **kwargs):
        prompt = f"# language: {language}\n# {message}\n"
        inputs = self._tokenizer.encode(prompt, return_tensors="pt").to(self._model.device)
        outputs = self._model.generate(inputs, max_length=256, top_k=1)  # 示例中使用greedy decoding，检查输出结果是否对齐
        return self._tokenizer.decode(outputs[0])

# TODO: 目前的自然语言生成代码已实现，但是无法识别整个项目中一些特定的词汇，达不到想要的效果。例如：进入首页、点击登录按钮。
# TODO: 有2个思路：
# TODO: 1. 使用jieba对输入的句子做预处理，根据配置的词库把一些特定的词语替换成实际的值。例如：检测到“首页”则替换成 “https://www,bilibili.com”。但是这种方法对于一些复杂的上下文可能不会太理解
# TODO: 2. 重新训练自然语言处理模型，让模型直接学习这些词语的含义。


if __name__ == '__main__':
    nc = NLP2Code()
    result = nc('封装一个函数，用于检测文件是否有被修改，函数接收两个参数：上次最后修改时间、文件路径。返回一个元组 (是否修改的bool值, '
                '新的最后修改时间)。如果传入的文件路径不存在直接抛出文件不存在的错误，注意错误提示要中文')
    print(result)


### 使用python的lex/yacc工具ply实现的json解析器

#### 环境
os: windows/mac/linux

python : python 2.7

#### 使用方法

```shell
pip install -r requirements.txt
```
将json_parser.py复制到需要的文件夹下
```python
import json_parser
json_string = '{"a": [-112.3, 1.02, [1, 2, 3], 3, "\\u4f60\\u597d"], "c": 1, "b": {"c": 1}, "e": 1234, "d": 1.2345}'
# 解析json字符串
json_dict_from_string = json_parser.loads(json_string)
print json_dict_from_string
# 解析json文件
json_dict_from_file = json_parser.load("test.json")
print json_dict_from_string
```

可以直接运行
```shell
python json_parser.py test.json
```
或者
```shell
python test.py
```

查看效果


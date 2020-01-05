# encoding=utf-8

import json_parser

json_string = '{"a": [-112.3, 1.02, [1, 2, 3], 3, "\\u4f60\\u597d"], "c": 1, "b": {"c": 1}, "e": 1234, "d": 1.2345}'

# 解析json字符串
json_dict_from_string = json_parser.loads(json_string)
print json_dict_from_string['a'][-1]

# 解析json文件
json_dict_from_file = json_parser.load("test.json")
print json_dict_from_string['a'][-1]
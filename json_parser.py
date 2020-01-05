# encoding=utf-8
# coded by nathanguo
# data: 2019-12-16
# usage: python json_parser.py filename


import ply
import ply.lex
import ply.yacc
import sys
import codecs

# 用于进行词法分析的token
JSON_TOKENS = [
    'BEGIN_ARRAY',  # 列表的起始符号 [
    'BEGIN_OBJECT',  # 对象的起始符号 {
    'END_ARRAY',  # 列表的终止符号 ]
    'END_OBJECT',  # 对象的终止符号 }
    'OBJECT_SEPARATOR',  # 用于分隔键和值得冒号 :
    'VALUE_SEPARATOR',  # 用于分隔列表中的元素 ,
    'QUOTATION_MARK',  # 引号，用于开启字符串的解析 "
    'FALSE',  # json中的false，对应python中的False
    'TRUE',  # json中的true，对应python中的True
    'NULL',  # json中的null，对应python中的None
    'DECIMAL_POINT',  # 浮点数中的小数点
    'DIGITS',  # 数字
    'E',  # 科学计数法中的e
    'MINUS',  # 减号
    'PLUS',  # 加号
    'ZERO',  # 0
    # 字符串可能有转义字符和非转义字符
    'UNESCAPED',  # 非转义字符
    'ESCAPE',  # 转义字符，当遇到 \ 时，进入转义状态
    # 常用转义字符
    'REVERSE_SOLIDUS',  # 反斜杠 \
    'SOLIDUS',  # 斜杠   /
    'BACKSPACE_CHAR',  # 空格
    'LINE_FEED_CHAR',  # 换行符  \n
    'CARRIAGE_RETURN_CHAR',  # 回车符 \r
    'TAB_CHAR',  # \t
    'UNICODE_HEX'  # unicode
]


class JsonLexer(object):
    '''
    用于对输入的json字符串进行词法分析的解析器
    '''

    def __init__(self, **kwargs):
        self.lexer = ply.lex.lex(module=self, **kwargs)

    # 词法分析所使用的所有token
    tokens = JSON_TOKENS

    # 词法分析有三种状态
    #
    #   默认状态下：
    #       用于解析对象，数组，数字等等
    #   字符串状态下:
    #       用于解析双引号下的字符串，由引号触发
    #   转义字符状态:
    #       此状态下字符处于转义状态，由 \ 触发
    #
    states = (
        ('string', 'exclusive'),
        ('escaped', 'exclusive')
    )

    # 默认状态下，跳过空格，tab，换行和\r
    t_ignore = ' \t\n\r'
    # 字符串状态下，不跳过任何字符
    t_string_ignore = ''
    # 转义状态下，不忽略任何字符
    t_escaped_ignore = ''

    # 默认状态下的词法规则
    t_BEGIN_ARRAY = r'\['  # '['
    t_BEGIN_OBJECT = r'\{'  # '{'
    t_END_ARRAY = r'\]'  # ']'
    t_END_OBJECT = r'\}'  # '}'
    t_OBJECT_SEPARATOR = r':'  # ':'
    t_VALUE_SEPARATOR = r','  # ','
    t_FALSE = r'false'  # 'false'
    t_TRUE = r'true'  # 'true'

    t_NULL = r'null'  # 'null'
    t_DECIMAL_POINT = r'\.'  # '.'
    t_DIGITS = r'[0-9]+'  # '0'..'9'
    t_E = r'[eE]'  # 'e' or 'E'
    t_MINUS = r'-'  # '-'
    t_PLUS = r'\+'  # '+'
    t_ZERO = r'0'  # '0'

    def t_ANY_error(self, t):
        """
        遇到不在范围内的字符的处理
        """
        last_cr = self.lexer.lexdata.rfind('\n', 0, t.lexpos)
        if last_cr < 0:
            last_cr = 0
        column = (t.lexpos - last_cr) + 1
        print "Illegal character '%s' at line %d pos %d" % (
            t.value[0], t.lineno, column)
        t.lexer.skip(1)

    # 当遇到冒号时，说明将进入字符串状态
    def t_QUOTATION_MARK(self, t):
        r'"'
        t.lexer.push_state('string')
        return t

    # 常见unicode字符
    def t_string_UNESCAPED(self, t):
        r'[\x20-\x21,\x23-\x5B,\x5D-\xFF]+'
        t.value = unicode(t.value, encoding='utf8')
        return t

    # 在字符串状态下，如果遇到"，则退出字符串状态
    def t_string_QUOTATION_MARK(self, t):
        r'"'
        t.lexer.pop_state()
        return t

    # 遇到斜杠时，进入转义状态
    def t_string_ESCAPE(self, t):
        r'\\'
        # 进入转义状态，使用栈来保存状态
        t.lexer.push_state('escaped')
        return t

    # 在转义状态下，遇到引号，表示引号为字面量，不具有特殊意义，同时退出转义状态
    def t_escaped_QUOTATION_MARK(self, t):
        r'"'
        t.lexer.pop_state()
        return t

    # 在转义状态下，遇到反斜杠，反斜杠为字面量，不具有特殊意义，同时退出转义状态
    def t_escaped_REVERSE_SOLIDUS(self, t):
        r'\\'
        t.lexer.pop_state()
        return t

    # 在转义状态下的反斜杠
    def t_escaped_SOLIDUS(self, t):
        r'/'
        t.lexer.pop_state()
        return t

    # 转义状态下的空格
    def t_escaped_BACKSPACE_CHAR(self, t):
        r'\ '
        t.lexer.pop_state()
        t.value = " "
        return t

    # 转义状态下的r
    def t_escaped_CARRIAGE_RETURN_CHAR(self, t):
        r'r'
        t.lexer.pop_state()
        t.value = '\r'
        return t

    # 转义状态下的n，表示换行
    def t_escaped_LINE_FEED_CHAR(self, t):
        r'n'
        t.lexer.pop_state()
        t.value = '\n'
        return t

    # 转义状态下的t，表示tab
    def t_escaped_TAB_CHAR(self, t):
        r't'
        t.lexer.pop_state()
        t.value = '\t'
        return t

    # unicode字符
    def t_escaped_UNICODE_HEX(self, t):
        r'u[\x30-\x39,\x41-\x46,\x61-\x66]{4}'
        t.lexer.pop_state()
        return t

    def tokenize(self, data, *args, **kwargs):
        """
        用于将输入字符串转变为token列表，并返回
        :param data: 输入字符串
        :param args:
        :param kwargs:
        :return:
        """
        self.lexer.input(data)
        tokens = list()
        while True:
            token = self.lexer.token()
            print token
            if not token:
                break
            tokens.append(token)
        return tokens


class JsonParser(object):
    """
    通过JsonLexer解析产生的token列表，结合json的语法，用于解析json字符串为python中的字典
    """

    def __init__(self, **kwargs):
        """
        初始化lexer和parser
        :param kwargs:
        """
        self.lexer = JsonLexer(**kwargs).lexer
        self.parser = ply.yacc.yacc(module=self, **kwargs)

    tokens = JSON_TOKENS

    # 输入的json字符串可能转变为对象或者列表
    def p_text(self, p):
        '''text : object
                | array'''
        p[0] = p[1]

    # json中的value可以是对象，列表，数字和字符串，此value可以表示键值对中的键，也可以表示json列表中的元素
    def p_value(self, p):
        '''value : object
                 | array
                 | number
                 | string'''
        p[0] = p[1]

    # json中的value的特殊情况 false
    def p_value_false(self, p):
        '''value : FALSE'''
        p[0] = False

    # json中的value的特殊情况 true
    def p_value_true(self, p):
        '''value : TRUE'''
        p[0] = True

    # json中的value的特殊情况 null
    def p_value_null(self, p):
        '''value : NULL'''
        p[0] = None

    # json中的列表对象values是逗号分隔的value
    def p_values(self, p):
        '''values :
                  | values VALUE_SEPARATOR value
                  | value'''
        if len(p) == 1:
            p[0] = list()
        elif len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    # json中的对象推导
    def p_object(self, p):
        '''object : BEGIN_OBJECT members END_OBJECT'''
        p[0] = dict(p[2])

    # json对象中的成员，以逗号分隔，可以为空
    def p_members(self, p):
        '''members :
                   | members VALUE_SEPARATOR member
                   | member'''
        if len(p) == 1:
            p[0] = list()
        elif len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    # json对象中的每个成员是用冒号分隔的键值对，此处表示为元组记录，之后汇总为列表然后用dict解析
    def p_member(self, p):
        '''member : string OBJECT_SEPARATOR value'''
        p[0] = (p[1], p[3])

    # json中列表以[开头，]结尾
    def p_array(self, p):
        '''array :  BEGIN_ARRAY values END_ARRAY'''
        p[0] = list(p[2])

    # json中的数字可以是整数，也可以是浮点数，都有正负之分，有不同的推导规则
    def p_number(self, p):
        '''number : integer
                  | float
                  | MINUS integer
                  | MINUS float'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = -p[2]

    def p_integer(self, p):
        '''integer : int'''
        p[0] = int(p[1])

    # 带有幂指数的整数
    def p_integer_exp(self, p):
        '''integer : int exp'''
        p[0] = p[1] * p[2]

    # 浮点数
    def p_number_float(self, p):
        '''float : int DECIMAL_POINT DIGITS'''
        p[0] = p[1] + float('.' + p[3])

    # 带有幂指数的浮点数
    def p_number_float_exp(self, p):
        '''float : float exp'''
        p[0] = p[1] * p[2]

    # 幂指数的解析，其中幂指数可以为正，可以为负，可以不带符号
    def p_number_exp(self, p):
        '''exp : E DIGITS
               | E PLUS DIGITS
               | E MINUS DIGITS'''
        if len(p) == 3:
            p[0] = 10 ** int(p[2])
        else:
            if p[2] == '+':
                p[0] = 10 ** int(p[3])
            else:
                p[0] = 10 ** int(-p[3])

    # 特殊数字0
    def p_int_zero(self, p):
        '''int : ZERO'''
        p[0] = int(0)

    # DIGITS可能以0开头，所以需要特殊处理
    def p_int_non_zero(self, p):
        '''int : DIGITS'''
        if p[1].startswith('0'):
            raise SyntaxError('Leading zeroes are not allowed.')
        p[0] = int(p[1])

    # json中的字符串
    def p_string(self, p):
        '''string : QUOTATION_MARK chars QUOTATION_MARK'''
        p[0] = p[2]

    def p_chars(self, p):
        '''chars :
                 | chars char'''
        if len(p) == 1:
            p[0] = unicode()
        else:
            p[0] = p[1] + p[2]

    # json字符串中的字符可以是普通字符，也可以是转义后的特殊字符
    def p_char(self, p):
        '''char : UNESCAPED
                | ESCAPE QUOTATION_MARK
                | ESCAPE REVERSE_SOLIDUS
                | ESCAPE SOLIDUS
                | ESCAPE BACKSPACE_CHAR
                | ESCAPE LINE_FEED_CHAR
                | ESCAPE CARRIAGE_RETURN_CHAR
                | ESCAPE TAB_CHAR'''
        p[0] = p[len(p) - 1]

    # 用于解析unicode字符，具有\uXXXX这样的形式
    def p_char_unicode_hex(self, p):
        '''char : ESCAPE UNICODE_HEX'''
        p[0] = unichr(int(p[2][1:], 16))

    def p_error(self, p):
        print "Syntax error at '%s'" % p

    # 触发json解析任务
    def parse(self, data, *args, **kwargs):
        """
        解析字符串为对应的python数据结构
        :param data: 输入字符串
        :param args:
        :param kwargs:
        :return: 对应的python数据结构，可以是字典，也可以是列表
        """
        return self.parser.parse(data, lexer=self.lexer, *args, **kwargs)


def loads(input_string, **kwargs):
    """
    类似python标准库中的json.loads方法，将json字符串解析为对应的python数据结构
    :param input_string: 输入的json字符串
    :return: 对应的python数据结构，可以为列表或者字典
    """
    json_parser = JsonParser(**kwargs)
    return json_parser.parse(data=input_string)


def load(json_filename, **kwargs):
    """
    类似python标准库中的json.load方法，将json文件名中的内容解析为对应的python数据结构
    :param filename: json文件名
    :return: 对应的python数据结构，可以为列表或者字典
    """
    # 指定编码格式为utf-8，防止因为操作系统不同带来的差异
    with codecs.open(json_filename, 'r') as f:
        data = f.read()
        return loads(data, **kwargs)


if __name__ == '__main__':
    filename = sys.argv[1]
    print load(filename, debug=0)

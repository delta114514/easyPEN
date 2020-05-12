import os
import lark

grammar = os.path.join(os.path.dirname(__file__), 'grammar.lark')


class NPENTrasnformer(lark.Transformer):
    # -------------------- literals --------------------
    def type_int(self, type_name):
        return '整数'

    def type_long(self, type_name):
        return '長整数'

    def type_float(self, type_name):
        return '実数'

    def type_bool(self, type_name):
        return '真偽'

    def type_str(self, type_name):
        return '文字列'

    def types(self, types):
        return types[0]

    def priority(self, items):
        return '({})'.format(', '.join(items))

    def str(self, string):
        return "「{}」".format(string[0].value[1:-1])

    def bool(self, items):
        return items[0].data

    def float(self, number):
        return number[0].value

    def number(self, number):
        return number[0].value

    def symbol(self, symbol):
        if len(symbol) == 1:
            return symbol[0]
        return '{}{}'.format(symbol[0], symbol[1])

    def index(self, items):
        return '[{}]'.format(', '.join(items))

    def priority(self, items):
        return '({})'.format(items[0])

    def mod(self, items):
        return '{} % {}'.format(items[0], items[1])

    def division(self, items):
        return '{} / {}'.format(items[0], items[1])

    def multiplication(self, items):
        return '{} * {}'.format(items[0], items[1])

    def and_(self, items):
        return '{} かつ {}'.format(items[0], items[1])

    def or_(self, items):
        return '{} または {}'.format(items[0], items[1])

    def not_(self, items):
        return '{} でない'.format(items[0])

    def test(self, items):
        op = {'lt': "<",
              'le': "<=",
              'gt': ">",
              'ge': ">=",
              'eq': "=",
              'ne': "!="}
        return '{} {} {}'.format(items[0], op[items[1]], items[2])

    def bitop(self, items):
        return items[0].data

    def function_call(self, items):
        if items[0] == 'input':
            return 'input({})'.format(', '.join(items[1:]))
        elif items[0] == 'print':
            return '{}を改行なしで表示する'.format(' と '.join(items[1:]))
        elif items[0] == 'println':
            return '{}を表示する'.format(' と '.join(items[1:]))
        else:
            return '{}({})'.format(items[0], ', '.join(items[1:]))

    def substraction(self, items):
        return '{} - {}'.format(items[0], items[1])

    def addition(self, items):
        return '{} + {}'.format(items[0], items[1])

    def break_state(self, items):
        return 'くり返しを抜ける'

    def for_state(self, items):
        if len(items) == 5:
            return {
                'open': '{} を {} から {} まで {} ずつ増やしながら，'.format(*items[:4]),
                'indent': items[-1],
                'close': 'を繰り返す'
            }
        else:
            return {
                'open': '{} を {} から {} まで 1 ずつ増やしながら，'.format(*items[:3]),
                'indent': items[-1],
                'close': 'を繰り返す'
            }

    def until_state(self, items):
        return {
            'open': '繰り返し,',
            'indent': [*items[1:]],
            'close': 'を，{} になるまで実行する'.format(items[0])
        }

    def while_state(self, items):
        return {
            'open': '{} の間，'.format(items[0]),
            'indent': [*items[1:]],
            'close': 'を繰り返す'
        }

    def else_(self, items):
        return {
            'open': 'を実行し，そうでなければ',
            'indent': [*items[:]],
            'close': '',
            'nl': False
        }

    def elif_(self, items):
        return {
            'open': 'を実行し，そうでなくもし {} ならば'.format(items[0]),
            'indent': [*items[1:]],
            'close': '',
            'nl': False
        }

    def optional_if(self, items):
        return items

    def if_state(self, items):
        result = []
        result.append({
            'nl': False,
            'open': 'もし {} ならば'.format(items[0]),
            'indent': [*items[1:-1]],
            'close': ''
        })
        result.extend(items[2])
        result[-1]['close'] = 'を実行する'
        return result

    def arg_declare(self, items):
        return '{} {}'.format(items[0], items[1])

    def args_declare(self, items):
        return ', '.join(items)

    def declare(self, items):
        return '{} {}'.format(items[0], ', '.join(items[1:]))

    def return_state(self, items):
        return '{} を返す'.format(items[0])

    def end_state(self, items):
        return '手続きを抜ける'

    def assignment(self, items):
        return '{} ← {}'.format(*items)

    def function(self, items):
        return {
            'open': '関数 {} {}({})'.format(items[0], items[1], items[2]),
            'indent': [*items[3:]],
            'close': '関数終了'
        }

    def procedure(self, items):
        return {
            'open': '手続き {}({})'.format(items[0], items[1]),
            'indent': [*items[2:]],
            'close': '手続き終了'
        }

    def program(self, items):
        return items


class Parser:
    def __init__(self, filename, output='out.pen', encoding='utf-8'):
        self.filename = filename
        self.output_ = output
        self.encoding = encoding
        self.parser = lark.Lark(open(grammar, 'r', encoding=self.encoding).read(), start='program', parser='lalr')

    def parse(self):
        self.parsed = NPENTrasnformer().transform(
            self.parser.parse(open(self.filename, 'r', encoding=self.encoding).read()))

    def prettify(self):
        result = []
        indent_str = '  | '

        def walk(statement, indent=0):
            if isinstance(statement, str) and statement:
                result.append(indent_str * indent + statement)
                result.append('\n')
            elif isinstance(statement, dict):
                walk(statement['open'], indent)
                walk(statement['indent'], indent + 1)
                walk(statement['close'], indent)
                if statement.get('nl', True):
                    result.append('\n')
            elif isinstance(statement, list):
                for state in statement:
                    walk(state, indent)

        walk(self.parsed)

        self.result = ''.join(result)

    def output(self):
        with open(self.output_, 'w', encoding=self.encoding) as f:
            f.write(self.result)

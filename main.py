from lark import Lark
import os
import re

def my_parce(code):
    with open("gram.lark") as file_gramm:
        grammar = file_gramm.read()
    # code = re.split(r'[ \n\t]', code)
    code = re.split(r'[ \t\f\r\n]+', code)
    code = ' '.join(code)
    for sym in ['=', '|', '<-', '?', ',', '(', ')', '!', '^', '_']:
        code = code.replace(f' {sym}', sym)
        code = code.replace(f'{sym} ', sym)
    code = code.strip()
    print(code)
    print('==============================================')
    parcer = Lark(grammar, start="start")
    return parcer.parse(code).pretty()



path_to_tests = 'examples'
for test_filename in sorted(os.listdir(path_to_tests))[:4]:
    with open(os.path.join(path_to_tests, test_filename)) as test_file:
        test = test_file.read()
    print(f"---------------- TEST {test_filename} ----------------")
    print(test)
    print(f"----------------------{len(test_filename) * '-'}-----------------")
    print(my_parce(test))
    print(f"----------------------{len(test_filename) * '-'}-----------------")


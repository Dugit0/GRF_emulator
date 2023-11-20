from lark import Lark
import os
import sys


def get_parser(gramm_name):
    with open(gramm_name) as file_gramm:
        grammar = file_gramm.read()
    return Lark(grammar, start="start")

def my_parce(code, gramm_name):
    parcer = get_parser(gramm_name)
    return parcer.parse(code)



# path_to_tests = 'examples'
# for test_filename in sorted(os.listdir(path_to_tests))[:4]:
#     with open(os.path.join(path_to_tests, test_filename)) as test_file:
#         test = test_file.read()
#     print(f"---------------- TEST {test_filename} ----------------")
#     test = test.split('!!!')
#     if len(test) != 2:
#         print("'!!!' is reserved", file=sys.stderr)
#         sys.exit(1)
#     definition, call = test[0], test[1]
#     print(f"----------------------{len(test_filename) * '-'}-----------------")
#     print(my_parce(definition, "def_gram.lark"))
#     print(my_parce(call, "call_gram.lark"))
#     print(f"----------------------{len(test_filename) * '-'}-----------------")

# with open('examples/000.txt') as test_file:
#     test = test_file.read()


class ArgsError(Exception):
    def __init__(self, expected, received):
        self.expected = expected
        self.received = received
    def __str__(self):
        return f"Number of arguments mismatch. Expected - {self.expected}. Received - {self.received}"


class Func:
    def __init__(self, n=1, name=None):
        self.n = n
        self.name = name
        self.call_func = lambda : None
    def __str__(self):
        return self.name
    def __call__(self, *args):
        if len(args) != self.n:
            raise ArgsError(self.n, len(args))
        return self.call_func(*args)


def func_o():
    res = Func(n=1, name='o')
    def new_func(*args):
        return 0
    res.call_func = new_func
    return res


def func_s():
    res = Func(n=1, name='s')
    def new_func(*args):
        return args[0] + 1
    res.call_func = new_func
    return res


def func_i(n, m):
    res = Func(n, f'i^{n}_{m}')
    def new_func(*args):
        return args[m - 1]
    res.call_func = new_func
    return res


def composition(func, *fargs):
    n = fargs[0].n
    for farg in fargs:
        if farg.n != n:
            print(f"In function {farg.name}", file=sys.stderr)
            raise ArgsError(n, farg.n)
    def new_func(*args):
        return func(*[farg(*args) for farg in fargs])
    res = Func(n)
    res.call_func = new_func
    return res


def recursion(base, func):
    if base.n + 2 != func.n:
        raise ArgsError(base.n + 2, func.n)
    def new_func(*args):
        if args[-1] == 0:
            # return base(*(args[:-1]))
            return base(*args[:-1])
        new_args = list(args[:])
        new_args[-1] = new_args[-1] - 1
        new_args.append(new_func(*new_args))
        return func(*new_args)
    res = Func(base.n + 1)
    res.call_func = new_func
    return res

def minimisation():
    pass



# Sum = I^1_1 <- s | I^3_3 |
fun = composition(func_s(), func_i(3, 3))
summ = recursion(func_i(1, 1), fun)
for i in range(1, 100):
    for j in range(1, 100):
        if summ(i, j) != i + j:
            print(f"Error! {i = }, {j = }")
            break

# test = """
# Sum = I^1_1 <- s | I^3_3 |
# Mul = o <- Sum | I^3_1 I^3_3 |
# # Pow = s | o | <- Mul | I^3_1 I^3_3 |
# !!!
# Pow(2, 5)
# """
# print(f"---------------- TEST 000 ----------------")
# test = test.split('!!!')
# if len(test) != 2:
#     print("'!!!' is reserved", file=sys.stderr)
#     sys.exit(1)
# definition, call = test[0], test[1]
# print(definition)
# # print(call)
# tree = my_parce(definition, "def_gram.lark")
# print(tree.pretty())
# print(tree)
# print('===================')
#
# print(tree.children)
#
#
# for i in tree.children:
#     print(i.data, sep='\n\n\n')
#     print('----')



































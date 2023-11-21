from lark import Lark
import os
import sys
from tqdm import tqdm


# -------------- Parcer functions --------------
def get_parser(gramm_name):
    with open(gramm_name) as file_gramm:
        grammar = file_gramm.read()
    return Lark(grammar, start="start")


def my_parce(code, gramm_name):
    parcer = get_parser(gramm_name)
    return parcer.parse(code)


# -------------- Custom exception --------------
class ArgsError(Exception):
    def __init__(self, expected, received):
        self.expected = expected
        self.received = received
    def __str__(self):
        return f"number of arguments mismatch. Expected - {self.expected}. Received - {self.received}"


class DefError(Exception):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return f"name '{self.name}' is not defined"

# -------------- Functions --------------
class Func:
    def __init__(self, n=1, name='Unnamed'):
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
    res = Func(1, 'o')
    def new_func(*args):
        return 0
    res.call_func = new_func
    return res


def func_s():
    res = Func(1, 's')
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


def func_const(const, n):
    res = Func(n, f'{const}^{n}')
    def new_func(*args):
        return const
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
    # TODO: write this!!!
    pass



test = """
# a = o
# a = s
# a = I^1_1
# a = myfunc
# a = 12^12
# a = o | s |
# a = o <- I^3_1
# a = o ? 12
Sum = I^1_1 <- s | I^3_3 |
Mul = o <- Sum | I^3_1 I^3_3 |
# Pow = s | o | <- Mul | I^3_1 I^3_3 |
!!!
Pow(2, 5)
"""

test = test.split('!!!')
if len(test) != 2:
    print("'!!!' is reserved", file=sys.stderr)
    sys.exit(1)

definition, call = test[0], test[1]
print(definition)

tree = my_parce(definition, "def_gram.lark")
print(tree.pretty())
print('===================')

def get_func(func_name):
    global definition_dict
    if func_name not in definition_dict.keys():
        raise DefError(func_name)
    # Возможна лажа с тем, что это ссылка на экземпляр!!!
    # Протестировать!!!
    return definition_dict[func_name]


def gen_func(tree):
    print(f"{tree.data.value = }")
    # print(f"name of tree = {tree.children[0].value}")
    if tree.data.value == 'name':
        if tree.children[0].value == 'o':
            return func_o()
        elif tree.children[0].value == 's':
            return func_s()
        else:
            return get_func(tree.children[0].value)
    elif tree.data.value == 'i':
        return func_i(*list(map(lambda a: int(a.value), tree.children)))
    elif tree.data.value == 'const':
        return func_const(*list(map(lambda a: int(a.value), tree.children)))
    elif tree.data.value == 'comp':
        return composition(*list(map(lambda a: gen_func(a), tree.children)))
    elif tree.data.value == 'rec':
        return recursion(*list(map(lambda a: gen_func(a), tree.children)))
    elif tree.data.value == 'min':
        return minimisation(*list(map(lambda a: gen_func(a), tree.children)))
    else:
        print("Unexpected!!!")
        print(tree)

definition_dict = {}
for def_tree in tree.children:
    name = def_tree.children[0].children[0].value
    func = gen_func(def_tree.children[1])
    func.name = name
    definition_dict[name] = func
    # print(func, repr(func))
    # print(*def_tree.children, sep="\n--\n")

    # definition[]
    print('----')


mull = definition_dict['Mul']
print(mull(9, 7))






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



























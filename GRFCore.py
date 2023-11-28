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
class Defined:
    func = {}

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

def minimisation(func, ind):
    # Test it!
    if ind > func.n:
        raise ArgsError(f"<= {func.n}", ind)
    def new_func(*args):
        y = 0
        while True:
            new_args = list(args[:ind - 1]) + [y] + list(args[ind - 1:-1])
            ans = args[-1]
            if func(*new_args) == ans:
                return y
            y += 1
    res = Func(func.n)
    res.call_func = new_func
    return res


def get_func(func_name):
    global definition_dict
    if func_name not in Defined.func.keys():
        raise DefError(func_name)
    # Возможна лажа с тем, что это ссылка на экземпляр!!!
    # Протестировать!!!
    return Defined.func[func_name]


def gen_func(tree):
    mod = tree.data
    if mod == 'name':
        name_val = tree.children[0].value
        if name_val == 'o':
            return func_o()
        elif name_val == 's':
            return func_s()
        else:
            return get_func(name_val)
    elif mod == 'i':
        return func_i(*list(map(lambda a: int(a.value), tree.children)))
    elif mod == 'const':
        return func_const(*list(map(lambda a: int(a.value), tree.children)))
    elif mod == 'comp':
        return composition(*list(map(lambda a: gen_func(a), tree.children)))
    elif mod == 'rec':
        return recursion(*list(map(lambda a: gen_func(a), tree.children)))
    elif mod == 'min':
        # if len(tree.children) != 2:
        #     raise 
        # print(tree)
        return minimisation(*[gen_func(tree.children[0]), int(tree.children[1].value), *tree.children[2:]])
        # return minimisation(*list(map(lambda a: gen_func(a), tree.children)))
    else:
        print("Unexpected node in AST", file=sys.stderr)
        print(tree, file=sys.stderr)
        sys.exit(1)


def parse_def(definition):
    tree = my_parce(definition, "def_gram.lark")
    print(tree.pretty())
    print('===================')
    for def_tree in tree.children:
        # print(def_tree.pretty())
        name = def_tree.children[0].children[0].value
        func = gen_func(def_tree.children[1])
        func.name = name
        Defined.func[name] = func
        print(func, repr(func))
        print('----')


def parse_call(call):
    ans = []
    tree = my_parce(call, "call_gram.lark")
    print(tree.pretty())
    print('===================')
    for call_tree in tree.children:
        call_body = call_tree.children[0]
        # print(call_tree.pretty())
        mod = call_body.data.value
        if mod == 'name':
            name_val = call_body.children[0].value
            if name_val == 'o':
                func = func_o()
            elif name_val == 's':
                func = func_s()
            else:
                func = get_func(name_val)
        elif mod == 'i':
            func = func_i(*list(map(lambda a: int(a.value), call_body.children)))
        elif mod == 'const':
            func = func_const(*list(map(lambda a: int(a.value), call_body.children)))
        else:
            print("Unexpected node in AST", file=sys.stderr)
            print(tree, file=sys.stderr)
            sys.exit(1)
        args = tuple(map(lambda a: int(a.value), call_tree.children[1:]))
        ans.append((func, args))
        # print('----')
    return tuple(ans)


# ------------- Тестироване грамматики -------------
# path_to_tests = 'examples'
# for test_filename in sorted(os.listdir(path_to_tests))[1:4]:
#     with open(os.path.join(path_to_tests, test_filename)) as test_file:
#         test = test_file.read()
#     print(f"---------------- TEST {test_filename} ----------------")
#     test = test.split('!!!')
#     if len(test) != 2:
#         print("'!!!' is reserved", file=sys.stderr)
#         sys.exit(1)
#     definition, call = test[0], test[1]
#     print(definition)
#     print(f"----------------------{len(test_filename) * '-'}-----------------")
#     print(my_parce(definition, "def_gram.lark").pretty())
#     # print(my_parce(call, "call_gram.lark"))
#     print(f"----------------------{len(test_filename) * '-'}-----------------")




if __name__ == "__main__":

#     test = """
# # a = o
# # a = s
# # a = I^1_1
# # a = myfunc
# # a = 12^12
# # a = o | s |
# # a = o <- I^3_1
# # a = o ? 12
# Sum = I^1_1 <- s | I^3_3 |
# Mul = o <- Sum | I^3_1 I^3_3 |
# # Pow = s | o | <- Mul | I^3_1 I^3_3 |
# !!!
# Sum(10, 10)
# Mul(9, 9)
# Sum(100, 0, 123)
# Mul(7, 9)
#     """

#     test = """
# Sum = I^1_1 <- s | I^3_3 |
# Mul = o <- Sum | I^3_1 I^3_3 |
# Pow = s | o | <- Mul | I^3_1 I^3_3 |
#
# !!!
# o(12313)
# s(123)
# I^5_2(1, 2, 3, 4, 5)
# 1231^2(123, 323)
# Pow(2, 5)
#     """
    test = """
F = s | I^2_1 |
G = F ? 1
!!!
F(3, 6)
G(3, 6)
    """

    test = test.split('!!!')
    if len(test) != 2:
        print("'!!!' is reserved", file=sys.stderr)
        sys.exit(1)

    definition, call = test[0], test[1]
    print(definition)
    parse_def(definition)
    print('================================')
    
    print(call)
    called_func = parse_call(call)
    print('============ RESULT ============')
    for func, args in called_func:
        print(func(*args))







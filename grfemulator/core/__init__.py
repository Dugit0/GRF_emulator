from lark import Lark
import importlib.resources
from . import grammars
import sys
import logging
# import traceback

logging.basicConfig(level=logging.WARNING, filename='log.log', filemode='w')

GLOBAL_DEBUG_LOG = ""


# -------------- Custom exception --------------
class CodeFormatError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ArgsError(Exception):
    """
    Exception raised when expected x arguments and received y (x != y).
    """
    def __init__(self, expected, received):
        self.expected = expected
        self.received = received

    def __str__(self):
        return (f"Number of arguments mismatch. Expected - {self.expected}."
                f" Received - {self.received}.")


class DefError(Exception):
    """
    Exception raised when function is not defined.
    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Name '{self.name}' is not defined."


# -------------- Parcer functions --------------
def get_parser(gramm_name):
    """
    Return parser by name of the grammar.
    """
    gramm_path = importlib.resources.files(grammars).joinpath(gramm_name)
    with gramm_path.open() as file_gramm:
        grammar = file_gramm.read()
    return Lark(grammar, start="start", parser='lalr')


def my_parce(code, gramm_name):
    """
    Return AST by code and name of the grammar.
    """
    code = code.strip()
    if code == "":
        raise CodeFormatError("Trying to parce empty code.")
    parcer = get_parser(gramm_name)
    return parcer.parse(code)


# -------------- Functions --------------
class Func:
    def __init__(self, n=1, name='Unnamed', operation='-'):
        self.n = n
        self.name = name
        self.show_call = False
        self.operation = operation
        self.children = []
        self.debug_log = ""

    def __str__(self):
        return self.name

    def __call__(self, *args):
        global GLOBAL_DEBUG_LOG
        if len(args) != self.n:
            raise ArgsError(self.n, len(args))
        if self.show_call:
            GLOBAL_DEBUG_LOG += (f"{self.name}"
                                 f"({', '.join(list(map(str, args)))})\n")
        if self.operation == 'composition':
            func = self.children[0]
            return func(*[f(*args) for f in self.children[1:]])
        elif self.operation == 'recursion':
            base, func = self.children[0], self.children[1]
            if args[-1] == 0:
                return base(*args[:-1])
            new_args = list(args[:])
            new_args[-1] = new_args[-1] - 1
            new_args.append(self.__call__(*new_args))
            return func(*new_args)
        elif self.operation == 'minimisation':
            y = 0
            while True:
                new_args = list(args[:]) + [y]
                if self.children[0](*new_args) == 0:
                    return y
                y += 1
        else:
            return self.children[0](*args)


# default_funcs = {
#         "Sum": Func(2, "Sum", lambda a, b: a + b),
#         "Mul": Func(2, "Mul", lambda a, b: a * b),
#         "Diff": Func(2, "Diff", lambda a, b: max(a - b, 0)),
#         "Div": Func(2, "Div", lambda a, b: 0 if b == 0 else a // b),
#         }

def func_o():
    res = Func(1, 'o', 'o')
    def new_func(*args):
        return 0
    res.children = [new_func,]
    return res


def func_s():
    res = Func(1, 's', 's')
    def new_func(*args):
        return args[0] + 1
    res.children = [new_func,]
    return res


def func_i(n, m):
    res = Func(n, f'I^{n}_{m}', f'I^{n}_{m}')
    def new_func(*args):
        return args[m - 1]
    res.children = [new_func,]
    return res


def func_const(const, n):
    res = Func(n, f'{const}^{n}', f'{const}^{n}')
    def new_func(*args):
        return const
    res.children = [new_func,]
    return res


def composition(func, *fargs):
    n = fargs[0].n
    if func.n != len(fargs):
        logging.error(f"In function {func.name}")
        raise ArgsError(func.n, len(fargs))
    for farg in fargs:
        if farg.n != n:
            # print(f"In function {farg.name}", file=sys.stderr)
            logging.error(f"In function {farg.name}")
            raise ArgsError(n, farg.n)
#     def new_func(*args):
#         return func(*[farg(*args) for farg in fargs])
    res = Func(n=n, operation='composition')
    res.children = [func] + list(fargs)
    return res


def recursion(base, func, optimizations=[]):
    if base.n + 2 != func.n:
        raise ArgsError(base.n + 2, func.n)
#     if 'Orec_to_for' not in optimizations:
#         def new_func(*args):
#             if args[-1] == 0:
#                 return base(*args[:-1])
#             new_args = list(args[:])
#             new_args[-1] = new_args[-1] - 1
#             new_args.append(new_func(*new_args))
#             return func(*new_args)
#     else:
#         def new_func(*args):
#             base_args = args[:-1]
#             result = base(*base_args)
#             for i in range(1, args[-1] + 1):
#                 result = func(*[*base_args, i - 1, result])
#             return result
    res = Func(n=base.n + 1, operation='recursion')
    res.children = [base, func]
    return res


def minimisation(func):
    if func.n == 0:
        raise ArgsError(f"<= 1", func.n)
#     def new_func(*args):
#         y = 0
#         while True:
#             new_args = list(args[:]) + [y]
#             if func(*new_args) == 0:
#                 return y
#             y += 1
    res = Func(n=func.n - 1, operation='minimisation')
    res.children = [func]
    return res


def get_func(func_name, func_dict):
    global definition_dict
    if func_name not in func_dict.keys():
        raise DefError(func_name)
    # Возможна лажа с тем, что это ссылка на экземпляр!!!
    # Протестировать!!!
    return func_dict[func_name]


def gen_func(tree, func_dict, optimizations):
    mod = tree.data
    if mod == 'name':
        name_val = tree.children[0].value
        if name_val == 'o':
            return func_o()
        elif name_val == 's':
            return func_s()
        else:
            return get_func(name_val, func_dict)
    elif mod == 'i':
        return func_i(*list(map(lambda a: int(a.value), tree.children)))
    elif mod == 'const':
        return func_const(*list(map(lambda a: int(a.value), tree.children)))
    elif mod == 'comp':
        return composition(*list(map(lambda a: gen_func(a, func_dict, optimizations),
                                     tree.children)))
    elif mod == 'rec':
        return recursion(*(list(map(lambda a: gen_func(a, func_dict, optimizations),
                                   tree.children)) + [optimizations]))
    elif mod == 'min':
        # if len(tree.children) != 2:
        #     raise
        return minimisation(*list(map(lambda a: gen_func(a, func_dict, optimizations),
                                      tree.children)))
        # return minimisation(*list(map(lambda a: gen_func(a), tree.children)))
    else:
        # print("Unexpected node in AST", file=sys.stderr)
        # print(tree, file=sys.stderr)
        logging.error(f"Unexpected node in AST\n{tree}")
        sys.exit(1)


def parse_code(code):
    labels = ["DEFINITION:\n", "CALL:\n"]
    if any(map(lambda label: code.find(label) == -1, labels)):
        raise CodeFormatError("The file was corrupted. The 'DEFINITION:' and "
                              "'CALL:' tags were not found.")
    ind1, ind2 = sorted(list(map(lambda label: code.find(label), labels)))
    definition, call = code[ind1:ind2].strip(), code[ind2:].strip()
    if definition.startswith("CALL:"):
        definition, call = call, definition
    return definition, call


def parse_def(definition, optimizations=[]):
    func_dict = {}
    tree = my_parce(definition, "def_grammar.lark")
    # print(tree.pretty())
    # print('===================')
    logging.info(tree.pretty())
    for def_tree in tree.children:
        # print(def_tree.pretty())
        name = def_tree.children[0].children[0].value
        func = gen_func(def_tree.children[1], func_dict, optimizations)
        func.name = name
        if "Ougly_hack" in optimizations:
            func = default_funcs.get(func.name, func)
        func_dict[name] = func
        # print(func, repr(func))
        # print('----')
        logging.info(f"{func} {repr(func)}")
    return func_dict


def parse_call(call, func_dict):
    ans = []
    tree = my_parce(call, "call_grammar.lark")
    # print(tree.pretty())
    # print('===================')
    logging.info(tree.pretty())
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
                func = get_func(name_val, func_dict)
        elif mod == 'i':
            func = func_i(*list(map(lambda a: int(a.value),
                                    call_body.children)))
        elif mod == 'const':
            func = func_const(*list(map(lambda a: int(a.value),
                                        call_body.children)))
        else:
            # print("Unexpected node in AST", file=sys.stderr)
            # print(tree, file=sys.stderr)
            logging.error(f"Unexpected node in AST\n{tree}")
            sys.exit(1)
        args = tuple(map(lambda a: int(a.value), call_tree.children[1:]))
        ans.append((func, args))
        # print('----')
    return tuple(ans)

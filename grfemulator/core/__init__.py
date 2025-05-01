from lark import Lark
import importlib.resources
from . import resources
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
    gramm_path = importlib.resources.files(resources).joinpath(gramm_name)
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
    def __init__(self, n=1, name='Unnamed', operation='-', optimizations=[]):
        self.n = n
        self.name = name
        self.show_call = False
        self.operation = operation
        self.optimizations = optimizations
        self.children = []
        self.debug_log = ""

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if ((self.operation == other.operation)
            and (len(self.children) == len(other.children))):
            if (len(other.children) == 1 and not isinstance(other.children[0], Func)):
                return True
            else:
                return all([self.children[i] == other.children[i]
                             for i in range(len(self.children))])
        else:
            return False

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
            if "Orec_to_for" not in self.optimizations:
                if args[-1] == 0:
                    return base(*args[:-1])
                new_args = list(args[:])
                new_args[-1] = new_args[-1] - 1
                new_args.append(self.__call__(*new_args))
                return func(*new_args)
            else:
                base_args = args[:-1]
                result = base(*base_args)
                for i in range(1, args[-1] + 1):
                    result = func(*[*base_args, i - 1, result])
                return result
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

def func_o(optimizations=[]):
    res = Func(1, 'o', 'o')
    def new_func(*args):
        return 0
    res.children = [new_func,]
    return res


def func_s(optimizations=[]):
    res = Func(1, 's', 's')
    def new_func(*args):
        return args[0] + 1
    res.children = [new_func,]
    return res


def func_i(n, m, optimizations=[]):
    res = Func(n, f'I^{n}_{m}', f'I^{n}_{m}')
    def new_func(*args):
        return args[m - 1]
    res.children = [new_func,]
    return res


def func_const(const, n, optimizations=[]):
    res = Func(n, f'{const}^{n}', f'{const}^{n}')
    def new_func(*args):
        return const
    res.children = [new_func,]
    return res


def composition(func, *fargs, optimizations=[]):
    n = fargs[0].n
    if func.n != len(fargs):
        logging.error(f"In function {func.name}")
        raise ArgsError(func.n, len(fargs))
    for farg in fargs:
        if farg.n != n:
            # print(f"In function {farg.name}", file=sys.stderr)
            logging.error(f"In function {farg.name}")
            raise ArgsError(n, farg.n)
    res = Func(n=n, operation='composition')
    res.children = [func] + list(fargs)
    return res


def recursion(base, func, optimizations=[]):
    if base.n + 2 != func.n:
        raise ArgsError(base.n + 2, func.n)
    res = Func(n=base.n + 1, operation='recursion', optimizations=optimizations)
    res.children = [base, func]
    return res


def minimisation(func, optimizations=[]):
    if func.n == 0:
        raise ArgsError(f"<= 1", func.n)
    res = Func(n=func.n - 1, operation='minimisation')
    res.children = [func]
    return res


def get_func(func_name, func_dict):
    global definition_dict
    if func_name not in func_dict.keys():
        raise DefError(func_name)
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
                                   tree.children))), optimizations=optimizations)
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


def no_opt_parse_def(definition):
    func_dict = {}
    tree = my_parce(definition, "def_grammar.lark")
    logging.info(tree.pretty())
    for def_tree in tree.children:
        name = def_tree.children[0].children[0].value
        func = gen_func(def_tree.children[1], func_dict, optimizations=[])
        func.name = name
        func_dict[name] = func
        logging.info(f"{func} {repr(func)}")
    return func_dict

def get_opportunistic_opt(optimizations=[]):
    base_funcs_path = importlib.resources.files(resources).joinpath("base_functions.grf")
    with base_funcs_path.open() as base_funcs_file:
        base_funcs_def = base_funcs_file.read()
    base_funcs = no_opt_parse_def(base_funcs_def)
    base, opt = [], []
    for name, func in base_funcs.items():
        match name:
            case "Sg":
                base.append(func)
                opt.append(Func(n=1,
                                name="Sg",
                                operation="-",
                                optimizations=optimizations))
                opt[-1].children = [lambda x: int(x > 0)]
            case "Nsg":
                base.append(func)
                opt.append(Func(n=1,
                                name="Nsg",
                                operation="-",
                                optimizations=optimizations))
                opt[-1].children = [lambda x: int(x == 0)]
            case "Sum":
                base.append(func)
                opt.append(Func(n=2,
                                name="Sum",
                                operation="-",
                                optimizations=optimizations))
                opt[-1].children = [lambda x, y: x + y]
            case "Diff":
                base.append(func)
                opt.append(Func(n=2,
                                name="Diff",
                                operation="-",
                                optimizations=optimizations))
                opt[-1].children = [lambda x, y: max(x - y, 0)]
            case "Mul":
                base.append(func)
                opt.append(Func(n=2,
                                name="Mul",
                                operation="-",
                                optimizations=optimizations))
                opt[-1].children = [lambda x, y: x * y]
            case "Div":
                base.append(func)
                opt.append(Func(n=2,
                                name="Div",
                                operation="-",
                                optimizations=optimizations))
                opt[-1].children = [lambda x, y: 0 if y == 0 else x // y]
    return base, opt


def opportunistic_replace(func, base_func, opt_func):
    if func == base_func:
        return opt_func
    for i in range(len(func.children)):
        if isinstance(func.children[i], Func):
            func.children[i] = opportunistic_replace(func.children[i], base_func, opt_func)
    return func


def parse_def(definition, optimizations=[]):
    func_dict = no_opt_parse_def(definition)
    if "Oopportunistic" in optimizations:
        base, opt = get_opportunistic_opt(optimizations=optimizations)
        for optimization_number in range(len(base) - 1, -1, -1):
            for name, func in func_dict.items():
                func_dict[name] = opportunistic_replace(func,
                                                        base[optimization_number],
                                                        opt[optimization_number])
    return func_dict

# def parse_def(definition, optimizations=[]):
#     func_dict = no_opt_parse_def(definition)
#     if "Oopportunistic" in optimizations:
#         base, opt = get_opportunistic_opt(optimizations=optimizations)
#         marks = {}
#         for name, func in func_dict.items():
#             for i in range(len(base)):
#                 if func == base[i]:
#                     marks[name] = i
#         for name in marks:
#             func_dict[name] = opt[marks[name]]
#     return func_dict


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

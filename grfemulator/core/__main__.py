import argparse
import sys
from . import parse_code, parse_def, parse_call, CodeFormatError

arg_parser = argparse.ArgumentParser(prog="grf core",
                                     description="Interpreter of grf files")
arg_parser.add_argument('filename')
arg_parser.add_argument('--Orec-to-for', action='store_true')
arg_parser.add_argument('--Ougly-hack', action='store_true')
args = arg_parser.parse_args()

with open(args.filename) as file_inp:
    code = file_inp.read()

optimizations = list(filter(lambda a: a.startswith('O') and vars(args)[a], vars(args).keys()))

try:
    definition, call = parse_code(code)
except CodeFormatError as e:
    print(e)
    sys.exit(1)

func_dict = parse_def(definition, optimizations)
called_func = parse_call(call, func_dict)
for func, args in called_func:
    print(func(*args))

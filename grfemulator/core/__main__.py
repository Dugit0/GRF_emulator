import argparse
import sys
from . import parse_code, parse_def, parse_call, CodeFormatError

arg_parser = argparse.ArgumentParser(prog="grf core",
                                     description="Interpreter of grf files")
arg_parser.add_argument('filename')
args = arg_parser.parse_args()

with open(args.filename) as file_inp:
    code = file_inp.read()

try:
    definition, call = parse_code(code)
except CodeFormatError as e:
    print(e)
    sys.exit(1)

func_dict = parse_def(definition)
called_func = parse_call(call, func_dict)
for func, args in called_func:
    print(func(*args))

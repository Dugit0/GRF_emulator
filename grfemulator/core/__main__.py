import argparse
import sys
from . import parse_def, parse_call

arg_parser = argparse.ArgumentParser(prog="grf core",
                                     description="Interpreter of grf files")

arg_parser.add_argument('filename')
args = arg_parser.parse_args()

with open(args.filename) as file_inp:
    code = file_inp.read()

code = code.split('!!!')
if len(code) != 2:
    print("File format error! '!!!' is reserved separator", file=sys.stderr)
    sys.exit(1)

definition, call = code[0], code[1]

func_dict = parse_def(definition)
called_func = parse_call(call, func_dict)

for func, args in called_func:
    print(func(*args))


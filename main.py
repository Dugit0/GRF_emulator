import pyparsing as pp
import os

"""
common_name -     <pp.identchars><pp.identbodychars>
I -               I^<nums>_<nums>
constant -        <nums>^<nums>
definition -      <func_name> = ...
composition -     ... | ...
recursion -       ... <- ...
minimisation -    ... ? <nums>
call -            !<func_name>(<zero or more: <nums>, <nums>, ...>)
open_bracket -    (
close_bracket -   )
"""
func_I = 'I' + pp.Suppress('^') + pp.Word(pp.nums) + pp.Suppress('_') + pp.Word(pp.nums)
func_I.set_name('I')
constant = pp.Word(pp.nums) + pp.Suppress('^') + pp.Word(pp.nums)
constant.set_name('constant')
func_name = pp.Word(pp.identchars, pp.identbodychars)
func_name.set_name('function')
all_functions = func_I ^ func_name ^ constant
definition = func_name + pp.Char('=')
composition = pp.Char('|')
recursion = pp.Literal('<-')
minimization = '?' + pp.Word(pp.nums)
func_call = '!' + all_functions + '(' + pp.Opt(pp.Word(pp.nums)) + pp.ZeroOrMore(pp.Suppress(',') + pp.Word(pp.nums)) + ')'
open_bracket = pp.Char('(')
close_bracket = pp.Char(')')
# expr = pp.Or([func_name, func_I, constant])
# expr = func_name ^ func_I ^ constant
expr = pp.ZeroOrMore(func_I ^ constant ^ func_name ^ definition ^ composition ^ recursion ^ minimization ^ func_call ^ open_bracket ^ close_bracket)



parser = expr
parser.ignore(pp.python_style_comment)   # Comment of the form # ... (to end of line)
parser.ignore(pp.c_style_comment)        # Comment of the form /* ... */
# parser.run_tests("""
#                  # asdfsa_asf323
#                  # asd21
#                  sdf434__
#                  asfsfa /* asdfasdf */
#                  __sd__ #asdfasf asfadf
#                  123^123 # sdfI^1_2
#                  0^0
#                  2^1
#                  I^113_341
#                  I^1233_321
#                  kkasdfaiafjaskd
#                  """)

# test = """
# F = asdf
# F = sdfa
# asd | a | s | v
# adfsf | aas <- sdf | asdf23
# asdf <- sdf <- sdfaf | sdf <- sdfadf
# asdfadf ? 234124
# asdf ? 1
# sdfadf | asdfa <- asdfa ? 323
# sg = o <- s | 0^2
# """
# parser.run_tests(test)

# res = parser.parse_file(os.path.join('examples', '001.txt'))
# print(res)


path_to_tests = 'examples'
for test_filename in sorted(os.listdir(path_to_tests)):
    with open(os.path.join(path_to_tests, test_filename)) as test_file:
        test = test_file.read()
    print(f"---------------- TEST {test_filename} ----------------")
    print(test)
    print(f"----------------------{len(test_filename) * '-'}-----------------")
    # print(parser.parse_string(test))
    parser.run_tests(test)
    # print(parser.run_tests(test))
    print(f"----------------------{len(test_filename) * '-'}-----------------")
    

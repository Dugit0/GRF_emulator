import main
import sys
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


if len(sys.argv) != 2:
    print(f"argc = {len(sys.argv)}. Expected 1", file=sys.stderr)
    sys.exit(1)

file_name = sys.argv[1]
with open(file_name) as file_inp:
    code = file_inp.read()

code = code.split('!!!')
if len(code) != 2:
    print("'!!!' is reserved", file=sys.stderr)
    sys.exit(1)

definition, call = code[0], code[1]

tree = main.my_parce(definition, "def_gram.lark")

for def_tree in tree.children:
    name = def_tree.children[0].children[0].value
    func = main.gen_func(def_tree.children[1])
    func.name = name
    main.Defined.func[name] = func

tree = main.my_parce(call, "call_gram.lark")

for call_tree in tree.children:
    name = call_tree.children[0].children[0].value
    args = list(map(lambda a: int(a.value), call_tree.children[1:]))
    print(main.get_func(name)(*args))

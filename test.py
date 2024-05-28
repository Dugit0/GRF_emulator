import sys
from grfemulator import core

definition = """
Nsg = s { 0^0 } <- 0^2
Sum = I^1_1 <- s { I^3_3 }
Mul = o <- Sum { I^3_1 I^3_3 }
ElDiff = 0^0 <- I^2_1
Diff = I^1_1 <- ElDiff { I^3_3 }
G = Sum { Nsg { Diff { Mul { s { I^4_3 } I^4_2 } I^4_1 } } I^4_4 }
F = 0^2 <- G
Div = F { I^2_1 I^2_2 I^2_1 }
Rest = Diff { I^2_1 Mul { I^2_2 Div } }
""".strip()

call = """
Rest(10, 4)
# Rest(15, 4)
# Rest(21, 11)
# Div(6, 3)
""".strip()



func_dict = core.parse_def(definition)
# print(func_dict['Div'].show_call)
func_dict['Div'].show_call = True
# func_dict['Rest'].show_call = True

called_func = core.parse_call(call, func_dict)

for func, args in called_func:
    print(func(*args))

print(core.GLOBAL_DEBUG_LOG)
# print(func_dict['Rest'].debug_log)

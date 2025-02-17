#include <cstdio>

unsigned const_0() {
    return 0;
}

unsigned const_0(unsigned x1) {
    return 0;
}

unsigned const_0(unsigned x1, unsigned x2) {
    return 0;
}

unsigned const_2(unsigned x1) {
    return 2;
}

unsigned I_1_1(unsigned x1) {
    return x1;
}

unsigned I_2_1(unsigned x1, unsigned x2) {
    return x1;
}

unsigned I_2_2(unsigned x1, unsigned x2) {
    return x2;
}

unsigned I_3_1(unsigned x1, unsigned x2, unsigned x3) {
    return x1;
}

unsigned I_3_2(unsigned x1, unsigned x2, unsigned x3) {
    return x2;
}

unsigned I_3_3(unsigned x1, unsigned x2, unsigned x3) {
    return x3;
}

unsigned I_4_1(unsigned x1, unsigned x2, unsigned x3, unsigned x4) {
    return x1;
}

unsigned I_4_2(unsigned x1, unsigned x2, unsigned x3, unsigned x4) {
    return x2;
}

unsigned I_4_3(unsigned x1, unsigned x2, unsigned x3, unsigned x4) {
    return x3;
}

unsigned I_4_4(unsigned x1, unsigned x2, unsigned x3, unsigned x4) {
    return x4;
}

unsigned s(unsigned x1) {
    return x1 + 1;
}

// # Сигнум
// Sg = 0^0 <- s { 0^2 };
unsigned Sg(unsigned x1) {
    if (x1 == 0) {
        return const_0();
    }
    return s(const_0(x1 - 1, Sg(x1 - 1)));
}
// # Отрицание сигнума
// Nsg = s { 0^0 } <- 0^2;
unsigned Nsg(unsigned x1) {
    if (x1 == 0) {
        return s(const_0());
    }
    x1--;
    return const_0(x1, Nsg(x1));
}
// # Сумма
// Sum = I^1_1 <- s { I^3_3 };
unsigned Sum(unsigned x1, unsigned x2) {
    if (x2 == 0) {
        return I_1_1(x1);
    }
    x2--;
    return s(I_3_3(x1, x2, Sum(x1, x2)));
}
// # Умножение
// Mul = o <- Sum { I^3_1, I^3_3 };
unsigned Mul(unsigned x1, unsigned x2) {
    if (x2 == 0) {
        return const_0(x1);
    }
    x2--;
    return Sum(I_3_1(x1, x2, Mul(x1, x2)), I_3_3(x1, x2, Mul(x1, x2)));
}
// # Вычитание единицы (-1)
// ElDiff = 0^0 <- I^2_1;
unsigned ElDiff(unsigned x1) {
    if (x1 == 0) {
        return const_0();
    }
    x1--;
    return I_2_1(x1, ElDiff(x1));
}

// # Вычитание
// Diff = I^1_1 <- ElDiff { I^3_3 };
unsigned Diff(unsigned x1, unsigned x2) {
    if (x2 == 0) {
        return I_1_1(x1);
    }
    x2--;
    return ElDiff(I_3_3(x1, x2, Diff(x1, x2)));
}
// G = Sum {
//          Nsg {
//               Diff {
//                     Mul {
//                          s { I^4_3 },
//                          I^4_2
//                     },
//                     I^4_1
//               }
//          },
//          I^4_4
//     };
unsigned G(unsigned x1, unsigned x2, unsigned x3, unsigned x4) {
    return Sum(
               Nsg(
                   Diff(
                        Mul(
                            s(I_4_3(x1, x2, x3, x4)),
                            I_4_2(x1, x2, x3, x4)
                        ),
                        I_4_1(x1, x2, x3, x4)
                   )
               ),
               I_4_4(x1, x2, x3, x4)
           );
}
// F = 0^2 <- G;
unsigned F(unsigned x1, unsigned x2, unsigned x3) {
    if (x3 == 0) {
        return const_0(x1, x2);
    }
    x3--;
    return G(x1, x2, x3, F(x1, x2, x3));
}
// # Деление
// Div = F { I^2_1, I^2_2, I^2_1 };
unsigned Div(unsigned x1, unsigned x2) {
    return F(I_2_1(x1, x2), I_2_2(x1, x2), I_2_1(x1, x2));
}
// # Остаток от деления
// Rest = Diff {
//              I^2_1,
//              Mul { I^2_2, Div }
//        };
unsigned Rest(unsigned x1, unsigned x2) {
    return Diff(I_2_1(x1, x2), Mul(I_2_2(x1, x2), Div(x1, x2)));
}
// # Divisibility(x, y) - делимость x на y
// Divisibility = Nsg { Rest };
unsigned Divisibility(unsigned x1, unsigned x2) {
    return Nsg(Rest(x1, x2));
}
// F1 = 0^1 <- Sum {
//                 Divisibility { I^3_1, I^3_2 },
//                 I^3_3
//            };
unsigned F1(unsigned x1, unsigned x2) {
    if (x2 == 0) {
        return const_0(x1);
    }
    x2--;
    return Sum(
               Divisibility(I_3_1(x1, x2, F1(x1, x2)), I_3_2(x1, x2, F1(x1, x2))),
               I_3_3(x1, x2, F1(x1, x2))
           );
}
// # Число делителей
// Num_of_divs = s { F1 { I^1_1, I^1_1 } };
unsigned Num_of_divs(unsigned x1) {
    return s(F1(I_1_1(x1), I_1_1(x1)));
}
// # Абсолютная разность
// AbsDiff = Sum {
//                Diff {
//                      I^2_1,
//                      I^2_2
//                },
//                Diff {
//                      I^2_2,
//                      I^2_1
//                }
//           };
unsigned AbsDiff(unsigned x1, unsigned x2) {
    return Sum(
               Diff(I_2_1(x1, x2), I_2_2(x1, x2)),
               Diff(I_2_2(x1, x2), I_2_1(x1, x2))
            );
}
// # Равно
// Equal = Nsg { AbsDiff };
unsigned Equal(unsigned x1, unsigned x2) {
    return Nsg(AbsDiff(x1, x2));
}
// # Неравно
// Not_equal = Sg { AbsDiff };
unsigned Not_equal(unsigned x1, unsigned x2) {
    return Sg(AbsDiff(x1, x2));
}
// # Меньше или равно
// Less_eq = Nsg { Diff { I^2_1, I^2_2 } };
unsigned Less_eq(unsigned x1, unsigned x2) {
    return Nsg(Diff(I_2_1(x1, x2), I_2_2(x1, x2)));
}
// # Является ли число простым
// Is_prime = Equal { Num_of_divs { I^1_1 }, 2^1 };
unsigned Is_prime(unsigned x1) {
    return Equal(Num_of_divs(I_1_1(x1)), const_2(x1));
}
// # Является ли число составным
// Is_not_prime = Not_equal { Num_of_divs { I^1_1 }, 2^1 };
unsigned Is_not_prime(unsigned x1) {
    return Not_equal(Num_of_divs(I_1_1(x1)), const_2(x1));
}
// # Min_prime_more_than(x) - минимальное простое число большее, чем x
// Min_prime_more_than = ? (Sum {
//                              Is_not_prime { I^2_2 },
//                              Less_eq {I^2_2, I^2_1}
//                         });
unsigned Min_prime_more_than(unsigned x1) {
    unsigned y = 0;
    while (true) {
        printf("y = %u\n", y);
        if (Sum(Is_not_prime(I_2_2(x1, y)), Less_eq(I_2_2(x1, y), I_2_1(x1, y))) == 0) {
            return y;
        }
        y++;
    }
}
// CALL:
// Min_prime_more_than(15);

int main(void) {
    printf("%u\n", Min_prime_more_than(15));
}

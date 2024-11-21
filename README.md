# GRF_emulator
GRF emulator - интерпретатор языка, который основан на частично рекурсивных
функциях и только на них.

# Запуск
Запуск производится командами
```
pipenv shell
python -m grfemulator
```

# Синтаксис языка

## Функции
### Тождественный ноль
`o` - одноместный тождественный 0, т.е. $o(x) = 0$.

Пример:
```
o
```
### Функция следования
`s` - функция следования, т.е. $s(x) = x + 1$.

Пример:
```
s
```
### Функция выбора
`I^<n>_<m>` - функция выбора с параметрами $n$ и $m$, т.е.
$I^n_m(x_1, \dots, x_n) = x_m$.

Пример:
```
I^5_2
```
Который обозначает:
$$I^5_2(x_1, \dots, x_5) = x_2$$
### Константные функции
- `0^<n>` - n-местный тождественный $0$, т.е. $o^n(x_1, \dots, x_n) = 0$. Иными
    словами это функция от $n$ переменных, возвращающая число $0$.
- `<const>^<n>` - n-местная тождественная константа $const$,
    т.е. $s(s(\dots s(o^n(x_1, \dots, x_n))\dots)) = const$, где $s$ применяется $const$ раз.
    Иными словами это функция от $n$ переменных, возвращающая число $const$.

Примеры:
```
0^3
42^1
150^123
```
Которые обозначают функции

$$o(x_1, x_2, x_3) = 0$$

$$42(x_1) = s(...s(o^1(x_1))...) = 42$$

$$150(x_1, \dots, x_{123}) = s(\dots s(o^{123}(x_1, \dots, x_{123}))\dots) = 150$$

## Операции над функциями
### Суперпозиция

Операция суперпозиции применяется к n-меcтной функции $f(y_1, \dots, y_n)$ 
и m-местным функциям $f_1(x_1, \dots, x_m), \dots, f_n(x_1, \dots, x_m)$. При этом
результатом суперпозиции является m-местная функция $g$.

$$g(x_1, \dots, x_m) = f(f_1(x_1, \dots, x_m), \dots, f_n(x_1, \dots, x_m))$$

`F {A, B, C, ..., Z}` - суперпозиция функции $F(x_a, \dots, x_z)$ и функций $A(x_1, \dots, x_k), \dots Z(x_1, \dots, x_k)$ для фиксированного $k$.

Пример. Пусть `X`, `Y`, и `Z` - двухместные функции, а `U` — трёхместная. Тогда
```
U {X, Y, Z}
```
Который обозначает:

$$U(X(x_1, x_2), Y(x_1, x_2), Z(x_1, x_2))$$

### Примитивная рекурсия
Результатом примитивной рекурсии над n-местной функцией $g(x_1, \dots, x_n)$
и $(n+2)$-местной функцией $h(x_1, \dots, x_n, x_{n+1}, x_{n+2})$ является $(n+1)$-местная
функция $f(x_1, \dots, x_n, x_{n+1})$.

$$f(x_1, \dots, x_n, 0) = g(x_1, \dots, x_n)$$
$$f(x_1, \dots, x_n, y + 1) = h(x_1, \dots, x_n, y, f(x_1, \dots, x_n, y))$$

Пример. Пусть `A` - двухместная функция, а `B` — четырехместная. Тогда примитивная рекурсия
обозначается так:
```
A <- B
```
Результатом такой операции является трёхместная функция (назовём её `R`):

$$R(a, b, 0) = A(a, b)$$

$$R(a, b, 1) = B(a, b, 0, R(a, b, 0)) = B(a, b, 0, A(a, b))$$

$$R(a, b, 2) = B(a, b, 1, R(a, b, 1)) = B(a, b, 0, B(a, b, 0, A(a, b)))$$

$$\dots$$

$$R(a, b, n) = B(a, b, n-1, R(a, b, n-1)) = B(a, b, n-1, B(\dots, B(a, b, 0, A(a, b)), \dots))$$

### Минимизация
Минимизация применяется к $(n+1)$-местной функции $f(x_1, \dots, x_n, x_{n+1})$.
Результатом является n-местная функция $g(x_1, \dots, x_n)$

$$g(x_1, \dots, x_n) = \min ( y : f(x_1, \dots, x_{n}, y) = 0 )$$

Пример. Пусть `F` - трехместная функция. Тогда минимизация обозначается так:
```
?F
```
Результатом такой операции является двухместная функция (назовём её `G`):

$G(x_1, x_2) = A$, если $F(x_1, x_2, A) = 0$ и $\forall B < A$ выполняется $F(x_1, x_2, B) \ne 0$.

Заметим, что может быть такое, что описанного значения $A$ не существует, т.к. $\forall A$ верно $F(x_1, x_2, A) \ne 0$.
В этом случае программа зацикливается!

## Создание новых функций
Возможно создание пользовательских функций с именами, которые возможны по
правилам языка Си.
```
F = s;
G = I^5_1;
```
Которые обозначают функции

$$F(x) = s(x)$$

$$G(x_1, x_2, x_3, x_4, x_5) = I^5_1(x_1, x_2, x_3, x_4, x_5)$$

## Вызов функций
Вызов функций производится в отдельном окне вызова функций, которое
по умолчанию расположено в правом верхнем углу.
Синтаксис вызова функций:
```
F(1, 2, 3, 10)
```
## Комментарии
Поддерживаются комментарии в формате Python и Си.
```
# Это комментарий
/*
Это многострочный комментарий
Это многострочный комментарий
Это многострочный комментарий
*/
```

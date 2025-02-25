{-# LANGUAGE BangPatterns #-}

const_0 :: Integer
const_0 = 0

const_2 :: Integer
const_2 = 2

i_1_1 :: Integer -> Integer
i_1_1 x1 = x1

i_2_1 :: Integer -> Integer -> Integer
i_2_1 x1 _x2 = x1

i_2_2 :: Integer -> Integer -> Integer
i_2_2 _x1 x2 = x2

i_3_1 :: Integer -> Integer -> Integer -> Integer
i_3_1 x1 _x2 _x3 = x1

i_3_2 :: Integer -> Integer -> Integer -> Integer
i_3_2 _x1 x2 _x3 = x2

i_3_3 :: Integer -> Integer -> Integer -> Integer
i_3_3 _x1 _x2 x3 = x3

i_4_1 :: Integer -> Integer -> Integer -> Integer -> Integer
i_4_1 x1 _x2 _x3 _x4 = x1

i_4_2 :: Integer -> Integer -> Integer -> Integer -> Integer
i_4_2 _x1 x2 _x3 _x4 = x2

i_4_3 :: Integer -> Integer -> Integer -> Integer -> Integer
i_4_3 _x1 _x2 x3 _x4 = x3

i_4_4 :: Integer -> Integer -> Integer -> Integer -> Integer
i_4_4 _x1 _x2 _x3 x4 = x4

s :: Integer -> Integer
s x1 = x1 + 1

sg :: Integer -> Integer
sg x1
  | x1 == 0 = const_0
  | otherwise = s const_0

nsg :: Integer -> Integer
nsg x1
  | x1 == 0 = s const_0
  | otherwise = const_0

sum' :: Integer -> Integer -> Integer
sum' x1 x2
  | x2 == 0 = i_1_1 x1
  | otherwise = s (i_3_3 x1 (x2 - 1) (sum' x1 (x2 - 1)))

mul :: Integer -> Integer -> Integer
mul x1 x2
  | x2 == 0 = const_0
  | otherwise = sum' (i_3_1 x1 (x2 - 1) (mul x1 (x2 - 1))) (i_3_3 x1 (x2 - 1) (mul x1 (x2 - 1)))

elDiff :: Integer -> Integer
elDiff x1
  | x1 == 0 = const_0
  | otherwise = i_2_1 (x1 - 1) (elDiff (x1 - 1))

diff :: Integer -> Integer -> Integer
diff x1 x2
  | x2 == 0 = i_1_1 x1
  | otherwise = elDiff (i_3_3 x1 (x2 - 1) (diff x1 (x2 - 1)))

g :: Integer -> Integer -> Integer -> Integer -> Integer
g x1 x2 x3 x4 =
  sum'
    ( nsg
        ( diff
            ( mul
                ( s (i_4_3 x1 x2 x3 x4))
                (i_4_2 x1 x2 x3 x4)
            )
            (i_4_1 x1 x2 x3 x4)
        )
    )
    (i_4_4 x1 x2 x3 x4)

f :: Integer -> Integer -> Integer -> Integer
f x1 x2 x3
  | x3 == 0 = const_0
  | otherwise = g x1 x2 (x3 - 1) (f x1 x2 (x3 - 1))

div' :: Integer -> Integer -> Integer
div' x1 x2 = f (i_2_1 x1 x2) (i_2_2 x1 x2) (i_2_1 x1 x2)

rest :: Integer -> Integer -> Integer
rest x1 x2 = diff (i_2_1 x1 x2) (mul (i_2_2 x1 x2) (div' x1 x2))

divisibility :: Integer -> Integer -> Integer
divisibility x1 x2 = nsg (rest x1 x2)

f1 :: Integer -> Integer -> Integer
f1 x1 x2
  | x2 == 0 = const_0
  | otherwise =
      sum'
        ( divisibility (i_3_1 x1 (x2 - 1) (f1 x1 (x2 - 1))) (i_3_2 x1 (x2 - 1) (f1 x1 (x2 - 1))))
        (i_3_3 x1 (x2 - 1) (f1 x1 (x2 - 1)))

num_of_divs :: Integer -> Integer
num_of_divs x1 = s (f1 (i_1_1 x1) (i_1_1 x1))

absDiff :: Integer -> Integer -> Integer
absDiff x1 x2 =
  sum'
    (diff (i_2_1 x1 x2) (i_2_2 x1 x2))
    (diff (i_2_2 x1 x2) (i_2_1 x1 x2))

equal :: Integer -> Integer -> Integer
equal x1 x2 = nsg (absDiff x1 x2)

not_equal :: Integer -> Integer -> Integer
not_equal x1 x2 = sg (absDiff x1 x2)

less_eq :: Integer -> Integer -> Integer
less_eq x1 x2 = nsg (diff (i_2_1 x1 x2) (i_2_2 x1 x2))

is_prime :: Integer -> Integer
is_prime x1 = equal (num_of_divs (i_1_1 x1)) (const_2)

is_not_prime :: Integer -> Integer
is_not_prime x1 = not_equal (num_of_divs (i_1_1 x1)) (const_2)

min_prime_more_than :: Integer -> Integer
min_prime_more_than x1 = minPrimeMoreThanHelper 0
  where
    minPrimeMoreThanHelper :: Integer -> Integer
    minPrimeMoreThanHelper y = do
      if sum' (is_not_prime (i_2_2 x1 y)) (less_eq (i_2_2 x1 y) (i_2_1 x1 y)) == 0
         then y
         else minPrimeMoreThanHelper (y + 1)

main :: IO ()
main = do
  print $ min_prime_more_than 50



-- Исследовать на min_prime_more_than(x) от x на текущей реализации, на оппортунистической оптимизации и на haskell

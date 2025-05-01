import unittest
from parameterized import parameterized, parameterized_class
from grfemulator import core

@parameterized_class(('optimizations'), [
    # ([],),
    # (['Orec_to_for'],),
    (['Oopportunistic'],),
])
class CoreTests(unittest.TestCase):
    def test_sg(self):
        definition = """
        DEFINITION:
        Sg = 0^0 <- s { 0^2 };
        """.strip()
        func_dict = core.parse_def(definition, optimizations=self.optimizations)
        for i in range(20):
            call = f"""
            CALL:
            Sg({i});
            """
            called_func = core.parse_call(call, func_dict)
            for func, args in called_func:
                self.assertEqual(func(*args), 0 if i == 0 else 1)


    def test_nsg(self):
        definition = """
        DEFINITION:
        Nsg = s { 0^0 } <- 0^2;
        """.strip()
        func_dict = core.parse_def(definition, optimizations=self.optimizations)
        for i in range(10):
            call = f"""
            CALL:
            Nsg({i});
            """.strip()
            called_func = core.parse_call(call, func_dict)
            for func, args in called_func:
                self.assertEqual(func(*args), 1 if i == 0 else 0)


    def test_sum(self):
        definition = """
        DEFINITION:
        Sum = I^1_1 <- s { I^3_3 };
        """.strip()
        func_dict = core.parse_def(definition, optimizations=self.optimizations)
        for i in range(10):
            for j in range(10):
                call = f"""
                CALL:
                Sum({i}, {j});
                """.strip()
                called_func = core.parse_call(call, func_dict)
                for func, args in called_func:
                    self.assertEqual(func(*args), i + j)


    def test_mul(self):
        definition = """
        DEFINITION:
        Sum = I^1_1 <- s { I^3_3 };
        Mul = o <- Sum { I^3_1, I^3_3 };
        """.strip()
        func_dict = core.parse_def(definition, optimizations=self.optimizations)
        for i in range(10):
            for j in range(10):
                call = f"""
                CALL:
                Mul({i}, {j});
                """.strip()
                called_func = core.parse_call(call, func_dict)
                for func, args in called_func:
                    self.assertEqual(func(*args), i * j)


    def test_diff(self):
        definition = """
        DEFINITION:
        ElDiff = 0^0 <- I^2_1;
        Diff = I^1_1 <- ElDiff { I^3_3 };
        """.strip()
        func_dict = core.parse_def(definition, optimizations=self.optimizations)
        for i in range(10):
            for j in range(10):
                call = f"""
                CALL:
                Diff({i}, {j});
                """.strip()
                called_func = core.parse_call(call, func_dict)
                for func, args in called_func:
                    self.assertEqual(func(*args), 0 if i < j else i - j)


    def test_absdiff_1(self):
        definition = """
        DEFINITION:
        Sum = I^1_1 <- s { I^3_3 };
        ElDiff = 0^0 <- I^2_1;
        Diff = I^1_1 <- ElDiff { I^3_3 };
        AbsDiff = Sum {
                      Diff {
                              I^2_1,
                              I^2_2
                           },
                      Diff {
                              I^2_2,
                              I^2_1
                           }
                      };
        """.strip()
        func_dict = core.parse_def(definition, optimizations=self.optimizations)
        for i in range(10):
            for j in range(10):
                call = f"""
                CALL:
                AbsDiff({i}, {j});
                """.strip()
                called_func = core.parse_call(call, func_dict)
                for func, args in called_func:
                    self.assertEqual(func(*args), abs(i - j))


    def test_absdiff_2(self):
        definition = """
        DEFINITION:
        Sum = I^1_1 <- s { I^3_3 };
        ElDiff = 0^0 <- I^2_1;
        Diff = I^1_1 <- ElDiff { I^3_3 };
        AbsDiff = Sum { Diff, Diff { I^2_2, I^2_1 } };
        """.strip()
        func_dict = core.parse_def(definition, optimizations=self.optimizations)
        for i in range(10):
            for j in range(10):
                call = f"""
                CALL:
                AbsDiff({i}, {j});
                """.strip()
                called_func = core.parse_call(call, func_dict)
                for func, args in called_func:
                    self.assertEqual(func(*args), abs(i - j))


    def test_absdiff_3(self):
        definition = """
        DEFINITION:
        Sum = I^1_1 <- s { I^3_3 };
        ElDiff = 0^0 <- I^2_1;
        Diff = I^1_1 <- ElDiff { I^3_3 };
        AbsDiff = Sum { Diff { I^2_1, I^2_2 }, Diff { I^2_2, I^2_1 } };
        """.strip()
        func_dict = core.parse_def(definition, optimizations=self.optimizations)
        for i in range(10):
            for j in range(10):
                call = f"""
                CALL:
                AbsDiff({i}, {j});
                """.strip()
                called_func = core.parse_call(call, func_dict)
                for func, args in called_func:
                    self.assertEqual(func(*args), abs(i - j))


    def test_div(self):
        definition = """
        DEFINITION:
        Nsg = s { 0^0 } <- 0^2;
        Sum = I^1_1 <- s { I^3_3 };
        Mul = o <- Sum { I^3_1, I^3_3 };
        ElDiff = 0^0 <- I^2_1;
        Diff = I^1_1 <- ElDiff { I^3_3 };
        G = Sum { Nsg { Diff { Mul { s { I^4_3 }, I^4_2 }, I^4_1 } }, I^4_4 };
        F = 0^2 <- G;
        Div = F { I^2_1, I^2_2, I^2_1 };
        """.strip()
        func_dict = core.parse_def(definition, optimizations=self.optimizations)
        for i in range(10):
            for j in range(10):
                call = f"""
                CALL:
                Div({i}, {j});
                """.strip()
                called_func = core.parse_call(call, func_dict)
                for func, args in called_func:
                    self.assertEqual(func(*args), i if j == 0 else i // j)


    def test_rest(self):
        definition = """
        DEFINITION:
        Nsg = s { 0^0 } <- 0^2;
        Sum = I^1_1 <- s { I^3_3 };
        Mul = o <- Sum { I^3_1, I^3_3 };
        ElDiff = 0^0 <- I^2_1;
        Diff = I^1_1 <- ElDiff { I^3_3 };
        G = Sum { Nsg { Diff { Mul { s { I^4_3 }, I^4_2 }, I^4_1 } }, I^4_4 };
        F = 0^2 <- G;
        Div = F { I^2_1, I^2_2, I^2_1 };
        Rest = Diff { I^2_1, Mul { I^2_2, Div } };
        """.strip()
        func_dict = core.parse_def(definition, optimizations=self.optimizations)
        for i in range(10):
            for j in range(10):
                call = f"""
                CALL:
                Rest({i}, {j});
                """.strip()
                called_func = core.parse_call(call, func_dict)
                for func, args in called_func:
                    self.assertEqual(func(*args), i if j == 0 else i % j)

    def test_comments(self):
        definition = """
        DEFINITION:
        # It's my comment
        Nsg = s { 0^0 } <- 0^2;
        # It's my comment 2
        Sum = I^1_1 <- s { I^3_3 };
        Mul = o <- Sum { I^3_1, I^3_3 }; # It's my comment 3
        ElDiff = 0^0 <- I^2_1;#It's my comment 4
        Diff = I^1_1 <- ElDiff { I^3_3 }; # It's my comment 5 # asdf #### asdfadf #
        G = Sum { Nsg { Diff { Mul { s { I^4_3 }, I^4_2 }, I^4_1 } }, I^4_4 };
        /* Comment 6 */
        F = 0^2 <- G;
        /* Comment 7
        Comment 7
        Comment 7
        Comment 7
        Comment 7
        */
        Div = F { I^2_1, I^2_2, I^2_1 };
        Rest = Diff { I^2_1, Mul { I^2_2, Div } };
        /*
        Comment 8
        Comment 8
        Comment 8
        Comment 8
        */
        """.strip()
        func_dict = core.parse_def(definition, optimizations=self.optimizations)
        for i in range(10):
            for j in range(10):
                call = f"""
                CALL:
                Rest({i}, {j});
                """.strip()
                called_func = core.parse_call(call, func_dict)
                for func, args in called_func:
                    self.assertEqual(func(*args), i if j == 0 else i % j)


if __name__ == "__main__":
    unittest.main()

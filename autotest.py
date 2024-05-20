import unittest
from grfemulator import core


class TestSg(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        definition = """
        Sg = 0^0 <- s { 0^2 }
        """.strip()
        core.parse_def(definition)
    def test_small_brute_force(self):
        for i in range(20):
            call = f"""
            Sg({i})
            """
            called_func = core.parse_call(call)
            for func, args in called_func:
                self.assertEqual(func(*args), 0 if i == 0 else 1)


class TestNsg(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        definition = """
        Nsg = s { 0^0 } <- 0^2 
        """.strip()
        core.parse_def(definition)
    def test_small_brute_force(self):
        for i in range(10):
            call = f"""
            Nsg({i})
            """
            called_func = core.parse_call(call)
            for func, args in called_func:
                self.assertEqual(func(*args), 1 if i == 0 else 0)


class TestAdd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        definition = """
        Sum = I^1_1 <- s { I^3_3 }
        """.strip()
        core.parse_def(definition)

    # def test_small_int_1(self):
    #     call = """
    #     Sum(1, 3)
    #     """.strip()
    #     called_func = core.parse_call(call)
    #     for func, args in called_func:
    #         self.assertEqual(func(*args), 4)

    def test_small_brute_force(self):
        for i in range(10):
            for j in range(10):
                call = f"""
                Sum({i}, {j})
                """.strip()
                called_func = core.parse_call(call)
                for func, args in called_func:
                    self.assertEqual(func(*args), i + j)


class TestMul(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        definition = """
        Sum = I^1_1 <- s { I^3_3 }
        Mul = o <- Sum { I^3_1 I^3_3 }
        """.strip()
        core.parse_def(definition)
    def test_small_brute_force(self):
        for i in range(10):
            for j in range(10):
                call = f"""
                Mul({i}, {j})
                """.strip()
                called_func = core.parse_call(call)
                for func, args in called_func:
                    self.assertEqual(func(*args), i * j)


class TestDiff(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        definition = """
        ElDiff = 0^0 <- I^2_1
        Diff = I^1_1 <- ElDiff { I^3_3 }
        """.strip()
        core.parse_def(definition)
    def test_small_brute_force(self):
        for i in range(10):
            for j in range(10):
                call = f"""
                Diff({i}, {j})
                """.strip()
                called_func = core.parse_call(call)
                for func, args in called_func:
                    self.assertEqual(func(*args), 0 if i < j else i - j)


class TestAbsDiff_1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        definition = """
        Sum = I^1_1 <- s { I^3_3 }
        ElDiff = 0^0 <- I^2_1
        Diff = I^1_1 <- ElDiff { I^3_3 }
        AbsDiff = Sum { 
                      Diff {
                              I^2_1
                              I^2_2
                           }
                      Diff {
                              I^2_2
                              I^2_1
                           }
                      }
        """.strip()
        core.parse_def(definition)
    def test_small_brute_force(self):
        for i in range(10):
            for j in range(10):
                call = f"""
                AbsDiff({i}, {j})
                """.strip()
                called_func = core.parse_call(call)
                for func, args in called_func:
                    self.assertEqual(func(*args), abs(i - j))


class TestAbsDiff_2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        definition = """
        Sum = I^1_1 <- s { I^3_3 }
        ElDiff = 0^0 <- I^2_1
        Diff = I^1_1 <- ElDiff { I^3_3 }
        AbsDiff = Sum { Diff Diff { I^2_2 I^2_1 } }
        """.strip()
        core.parse_def(definition)
    def test_small_brute_force(self):
        for i in range(10):
            for j in range(10):
                call = f"""
                AbsDiff({i}, {j})
                """.strip()
                called_func = core.parse_call(call)
                for func, args in called_func:
                    self.assertEqual(func(*args), abs(i - j))


class TestAbsDiff_3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        definition = """
        Sum = I^1_1 <- s { I^3_3 }
        ElDiff = 0^0 <- I^2_1
        Diff = I^1_1 <- ElDiff { I^3_3 }
        AbsDiff = Sum { Diff { I^2_1 I^2_2 } Diff { I^2_2 I^2_1 } }
        """.strip()
        core.parse_def(definition)
    def test_small_brute_force(self):
        for i in range(10):
            for j in range(10):
                call = f"""
                AbsDiff({i}, {j})
                """.strip()
                called_func = core.parse_call(call)
                for func, args in called_func:
                    self.assertEqual(func(*args), abs(i - j))


class TestDiv(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        definition = """
        Nsg = s { 0^0 } <- 0^2 
        Sum = I^1_1 <- s { I^3_3 }
        Mul = o <- Sum { I^3_1 I^3_3 }
        ElDiff = 0^0 <- I^2_1
        Diff = I^1_1 <- ElDiff { I^3_3 }
        G = Sum { Nsg { Diff { Mul { s { I^4_3 } I^4_2 } I^4_1 } } I^4_4 }
        F = 0^2 <- G
        Div = F { I^2_1 I^2_2 I^2_1 }
        """.strip()
        core.parse_def(definition)
    def test_small_brute_force(self):
        for i in range(10):
            for j in range(10):
                call = f"""
                Div({i}, {j})
                """.strip()
                called_func = core.parse_call(call)
                for func, args in called_func:
                    self.assertEqual(func(*args), i if j == 0 else i // j)


class TestRest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        core.parse_def(definition)
    def test_small_brute_force(self):
        for i in range(10):
            for j in range(10):
                call = f"""
                Rest({i}, {j})
                """.strip()
                called_func = core.parse_call(call)
                for func, args in called_func:
                    self.assertEqual(func(*args), i if j == 0 else i % j)


if __name__ == "__main__":
    unittest.main()

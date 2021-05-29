import os
import unittest

from lambdarado._lambdarado import _is_true_environ


class TestEnviron(unittest.TestCase):
    def test_true(self):
        os.environ["aaa"] = " tRuE "
        self.assertTrue(_is_true_environ("aaa"))

    def test_false(self):
        os.environ["aaa"] = " FaLsE "
        self.assertFalse(_is_true_environ("aaa"))

    def test_zero(self):
        os.environ["aaa"] = " 0 "
        self.assertFalse(_is_true_environ("aaa"))

    def test_zerozero(self):
        os.environ["aaa"] = " 00 "
        self.assertFalse(_is_true_environ("aaa"))

    def test_nonzero(self):
        os.environ["aaa"] = "23"
        self.assertTrue(_is_true_environ("aaa"))

    def test_one(self):
        os.environ["one"] = " 1 "
        self.assertTrue(_is_true_environ("one"))

    def test_labuda_default_true(self):
        os.environ["one"] = "labuda"
        self.assertTrue(_is_true_environ("one", default=True))

    def test_labuda_default_false(self):
        os.environ["one"] = "labuda"
        self.assertFalse(_is_true_environ("one", default=False))

    def test_none_default_true(self):
        try:
            del os.environ["one"]
        except KeyError:
            pass
        self.assertTrue(_is_true_environ("one", default=True))

    def test_none_default_false(self):
        try:
            del os.environ["one"]
        except KeyError:
            pass
        self.assertFalse(_is_true_environ("one", default=False))


if __name__ == "__main__":
    unittest.main()
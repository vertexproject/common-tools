import shutil
import tempfile
import unittest
import contextlib

class TstBase(unittest.TestCase):

    @contextlib.contextmanager
    def getTempdir(self):
        tempdir = tempfile.mkdtemp()
        try:
            yield tempdir
        finally:
            shutil.rmtree(tempdir)

    def eq(self, a, b):
        self.assertEqual(a, b)

    def ne(self, a, b):
        self.assertNotEqual(a, b)

    def len(self, n, obj):
        self.eq(n, len(obj))

    def true(self, expr):
        self.assertTrue(expr)

    def false(self, expr):
        self.assertFalse(expr)

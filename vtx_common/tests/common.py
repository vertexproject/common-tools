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

    def nn(self, x, msg=None):
        '''
        Assert X is not None
        '''
        self.assertIsNotNone(x, msg=msg)

    def none(self, x, msg=None):
        '''
        Assert X is None
        '''
        self.assertIsNone(x, msg=msg)

    def raises(self, *args, **kwargs):
        '''
        Assert a function raises an exception.
        '''
        return self.assertRaises(*args, **kwargs)

    def isinstance(self, obj, cls, msg=None):
        '''
        Assert a object is the instance of a given class or tuple of classes.
        '''
        self.assertIsInstance(obj, cls, msg=msg)

    def isin(self, member, container, msg=None):
        '''
        Assert a member is inside of a container.
        '''
        self.assertIn(member, container, msg=msg)

    def notin(self, member, container, msg=None):
        '''
        Assert a member is not inside of a container.
        '''
        self.assertNotIn(member, container, msg=msg)

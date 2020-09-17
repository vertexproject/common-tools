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

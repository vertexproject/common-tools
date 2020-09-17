import os

import vtx_common.utils as v_utils
import vtx_common.tests.common as t_common

class TestUtils(t_common.TstBase):

    def test_gitdir(self):

        with self.getTempdir() as dirn:
            self.assertFalse(v_utils.reqGitDir(dirn))
            os.makedirs(os.path.join(dirn, '.git'))
            self.assertTrue(v_utils.reqGitDir(dirn))

    def test_system(self):
        cwd = os.getcwd()
        buf = v_utils.system('pwd')
        system_pwd = buf.decode()
        system_pwd = system_pwd.strip()
        self.assertEqual(cwd, system_pwd)

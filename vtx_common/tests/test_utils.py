import os

import vtx_common.utils as v_utils
import vtx_common.tests.common as t_common

class TestUtils(t_common.TstBase):

    def test_gitdir(self):

        with self.getTempdir() as dirn:
            self.false(v_utils.reqGitDir(dirn))
            os.makedirs(os.path.join(dirn, '.git'))
            self.true(v_utils.reqGitDir(dirn))

    def test_system(self):
        cwd = os.getcwd()
        buf = v_utils.system('pwd')
        system_pwd = buf.decode()
        system_pwd = system_pwd.strip()
        self.eq(cwd, system_pwd)

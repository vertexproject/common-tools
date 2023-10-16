import os
import asyncio

import vtx_common.utils as v_utils
import vtx_common.tests.common as t_common
try:
    import vtx_common.tools.buildpkg as vt_buildpkg
except ImportError:
    vt_buildpkg = None

curdir = os.path.split(__file__)[0]
testpkgdir = os.path.join(curdir, 'testpkg')
testpkgfp = os.path.join(testpkgdir, 'testpkg.yaml')

class TestBuildpkg(t_common.TstBase):
    def test_buildpkg(self):
        if vt_buildpkg.s_common is None:
            self.skipTest('Synapse library is unavailable to test buildpkg tool with.')

        self.true(os.path.isfile(testpkgfp))
        argv = [testpkgfp, ]
        r = asyncio.run(vt_buildpkg.main(argv))
        self.eq(r, 0)

        import synapse.common as s_common

        pkgdef = s_common.yamlload(testpkgfp)
        efiles = set()
        for dnfo in pkgdef.get('docs'):
            bname = os.path.basename(dnfo.get('path'))
            efiles.add(bname)
            efiles.add(bname.rsplit('.', 1)[0] + '.rst')
        builddir = os.path.join(testpkgdir, 'docs', '_build')
        self.eq(efiles, set(os.listdir(builddir)))

        text = s_common.getbytes(os.path.join(builddir, 'bar.md')).decode()
        self.notin(':orphan:', text)
        self.notin(':tocdepth:', text)

        text = s_common.getbytes(os.path.join(builddir, 'stormpackage.md')).decode()
        # todo: test
        # https://pandoc.org/try/?params=%7B%22text%22%3A%22term+one%5Cn++++this+is+def+one+one%5Cn%5Cn++++this+is+def+one+two%5Cn%5Cnterm+two%5Cn++++this+is+def+two+one%22%2C%22to%22%3A%22markdown%22%2C%22from%22%3A%22rst%22%2C%22standalone%22%3Afalse%2C%22embed-resources%22%3Afalse%2C%22table-of-contents%22%3Afalse%2C%22number-sections%22%3Afalse%2C%22citeproc%22%3Afalse%2C%22html-math-method%22%3A%22plain%22%2C%22wrap%22%3A%22auto%22%2C%22highlight-style%22%3Anull%2C%22files%22%3A%7B%7D%2C%22template%22%3Anull%7D

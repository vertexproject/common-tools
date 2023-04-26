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

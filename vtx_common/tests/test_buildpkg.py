import io
import os
import sys
import json
import asyncio

import vtx_common.tests.common as t_common
try:
    import vtx_common.tools.buildpkg as vt_buildpkg
    import vtx_common.tools.pandoc_filter as vt_pandoc_filter
except ImportError:
    vt_buildpkg = None
    vt_pandoc_filter = None

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
        self.isin(':   baz (str): The baz.', text)
        self.isin(':   Baz the bam:\n\n        yield $lib.import(apimod).search(bam)', text)

        # pandoc api version check coverage

        old_stdin = sys.stdin

        try:
            sys.stdin = io.StringIO(json.dumps({'pandoc-api-version': [2, 0, 0]}))
            with self.raises(Exception) as ectx:
                vt_pandoc_filter.main()
            self.isin('does not match required version', str(ectx.exception))
        finally:
            sys.stdin = old_stdin

        # pandoc failure

        oldv = vt_buildpkg.PANDOC_FILTER

        try:
            vt_buildpkg.PANDOC_FILTER = os.path.join(curdir, 'newp.py')
            self.raises(AssertionError, asyncio.run, vt_buildpkg.main(argv))
        finally:
            vt_buildpkg.PANDOC_FILTER = oldv

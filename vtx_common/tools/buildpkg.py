import os
import sys
import json
import shutil
import asyncio
import logging
import argparse

try:
    import regex as re
    import synapse.common as s_common
    import synapse.tools.rstorm as s_rstorm
    import synapse.tools.autodoc as s_autodoc
except ImportError:
    import re
    s_common = None
    s_rstorm = None
    s_autodoc = None

logger = logging.getLogger(__name__)

logging.getLogger('vcr').setLevel(logging.WARNING)

# see https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html#file-wide-metadata
re_sphinx_metadata_fields = re.compile(r'^:(tocdepth|nocomments|orphan|nosearch):( \w+)?\n\n', flags=re.MULTILINE)

def hasPandoc():
    if os.system('pandoc --version') == 0:
        return True
    return False

async def buildPkgDocs(opts):

    pkgpath = opts.pkgfile
    logger.info(f'Building pkg for {pkgpath}')
    pkgdef = s_common.yamlload(pkgpath)
    assert pkgdef is not None

    dirn = os.path.dirname(s_common.genpath(pkgpath))

    docsdir = os.path.join(dirn, 'docs')
    builddir = os.path.join(dirn, 'docs', '_build')

    shutil.rmtree(builddir, ignore_errors=True)

    s_common.gendir(builddir)

    # touch any files we need in order to load a package, due to
    # rstorm needing to load the package using genpkg tool. This
    # does mean that standalone builds of a storm package from this
    # repo must be done after using this buildpkg tool.
    stormpkg_md_present = False
    for dnfo in pkgdef.get('docs', ()):
        fpath = dnfo.get('path')
        with s_common.genfile(dirn, fpath) as fd:
            pass
        if fpath.endswith('stormpackage.md'):
            stormpkg_md_present = True

    # Generate the build .RST for stormpackage.md
    if stormpkg_md_present:
        logger.info(f'Generating stormpkg.rst for {pkgpath}')
        pkgdocs, pkgname = await s_autodoc.docStormpkg(pkgpath)
        with s_common.genfile(docsdir, 'stormpackage.rst') as fd:
            text = pkgdocs.getRstText()
            if opts.rst_only is False:
                # Leave this in place if we're only generating RST
                text = text.replace('.. highlight:: none\n', '')
            fd.write(text.encode())
        logger.info('Generated the stormpackage.rst file!')

    for name in os.listdir(docsdir):

        if not name.endswith('.rst'):
            continue

        docpath = os.path.join(docsdir, name)

        basename = name.rsplit('.', 1)[0]

        builtmd = os.path.join(builddir, f'{basename}.md')
        builtrst = os.path.join(builddir, name)

        argv = (docpath, '--save', builtrst)
        logger.info(f'Executing rstorm for {argv}')
        await s_rstorm.main(argv)

        if opts.rst_only:
            logger.info(f'rst_only enabled, done processing {name}')
            continue

        logger.info('Preprocessing rstorm output')
        with s_common.genfile(builtrst) as fd:
            buf = fd.read().decode()

        # Remove highglight:: none directives
        buf = buf.replace('.. highlight:: none\n', '')

        # Remove sphinx metadata fields
        buf = re_sphinx_metadata_fields.sub('', buf)

        lines = buf.splitlines(keepends=True)

        # Remove lines which start with explicit sphinx rst targets
        nlines1 = []
        for line in lines:
            if line.startswith('.. _') and line.strip().endswith(':'):
                logger.info(f'Dropping: [{line.strip()}]')
                continue
            nlines1.append(line)

        buf = ''.join(nlines1)

        with s_common.genfile(builtrst) as fd:
            fd.truncate()
            _ = fd.write(buf.encode())

        logger.info(f'Converting {builtrst} to markdown')
        os.system(f'pandoc -f rst -t markdown -o {builtmd} {builtrst}')

        logger.info(f'Done converting {builtrst} to {builtmd}')

        # Strip out / manipupate the md content
        with s_common.genfile(builtmd) as fd:
            buf = fd.read().decode()

        lines = buf.splitlines(keepends=True)

        # Remove lines which only have a single `:` left in them
        nlines1 = [line for line in lines if line.strip() != ':']

        buf = ''.join(nlines1)

        with s_common.genfile(builtmd) as fd:
            fd.truncate()
            _ = fd.write(buf.encode())

        logger.info('Done manipulating markdown')

    logger.info(f'buildPkgDocs complete for {pkgpath}.')

prog = 'vtx_common.tools.buildpkg'
desc = 'A tool for building storm-package docs.'

async def main(argv):

    if s_common is None:
        logger.error('The synapse package must be installed to use the {prog} tool.')
        return 1

    pars = argparse.ArgumentParser(prog=prog, description=desc)
    pars.add_argument('pkgfile', metavar='<pkgfile>', help='Path to a storm package prototype yml file.')
    pars.add_argument('--rst-only', default=False, action='store_true',
                      help='Stops building after the .rst files have been generated.')

    opts = pars.parse_args(argv)

    if opts.rst_only is False and not hasPandoc():
        logger.error('Pandoc is not available, can only run rst/rstorm output.')
        return 1

    await buildPkgDocs(opts)

    return 0

if __name__ == '__main__': # pragma: no cover
    s_common.setlogging(logger, 'DEBUG')
    sys.exit(asyncio.run(main(sys.argv[1:])))

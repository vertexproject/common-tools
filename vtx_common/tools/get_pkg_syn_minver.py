import os
import sys
import asyncio
import logging
import argparse

import packaging.specifiers as p_specifiers

import yaml

logger = logging.getLogger(__name__)


def yamlload(fp):
    with open(fp, mode='rb') as fd:
        byts = fd.read()
    if not byts:
        return None
    return yaml.safe_load(byts.decode('utf8'))

def getMessageFromPkg(pkg, mtyp):
    reqv = pkg.get('synapse_version')
    minv = pkg.get('synapse_minversion')
    if minv:
        assert len(minv) == 3
        minv = [str(v) for v in minv]
        minv = '.'.join(minv)

        hasmin = False
        fullspec = p_specifiers.SpecifierSet()

        if reqv:
            specs = p_specifiers.SpecifierSet(reqv)
            for spec in specs:
                if spec.operator in (">", ">="):
                    hasmin = True
                    if spec.contains(minv):
                        fullspec = fullspec & f">={minv}"
                        continue

                fullspec = fullspec & str(spec)

        if not hasmin:
            fullspec = fullspec & f">={minv}"

        mesg = f'{mtyp} requires Synapse version {fullspec}.'
    elif reqv:
        mesg = f'{mtyp} requires Synapse version {reqv}.'
    else:
        mesg = f'{mtyp} has no Synapse version requirement specified.'
    return mesg


def main(argv):
    pars = makeargparser()
    opts = pars.parse_args(argv)

    assert os.path.isfile(opts.file)
    pkg = yamlload(opts.file)
    assert pkg is not None
    mesg = getMessageFromPkg(pkg, opts.type)
    print(mesg)
    return 0

def makeargparser():
    desc = 'Extract a minimum version string from a storm package.'
    pars = argparse.ArgumentParser('vtx_common.tools.get_pkg_syn_minver', description=desc)

    pars.add_argument('file', type=str,
                      help='Storm package file to extract from.')
    pars.add_argument('-t', '--type', action='store', type=str, required=True,
                      help='string type to print')

    return pars


if __name__ == '__main__':  # pragma: no cover
    main(sys.argv[1:])

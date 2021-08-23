import os
import sys
import asyncio
import logging
import argparse

import yaml

logger = logging.getLogger(__name__)


def yamlload(fp):
    with open(fp, mode='rb') as fd:
        byts = fd.read()
    if not byts:
        return None
    return yaml.safe_load(byts.decode('utf8'))

def getMessageFromPkg(pkg, mtyp):
    minv = pkg.get('synapse_minversion')
    if minv:
        assert len(minv) == 3
        minv = [str(v) for v in minv]
        minv = '.'.join(minv)
        mesg = f'The {mtyp} requires a minimum Synapse version of {minv} or greater.'
    else:
        mesg = f'The {mtyp} has no minimum Synapse version specified.'
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
    pars.add_argument('-t', '--type', action='store', choices=['Storm Service', 'Power-Up'], type=str, required=True,
                      help='string type to print')

    return pars


if __name__ == '__main__':  # pragma: no cover
    main(sys.argv[1:])

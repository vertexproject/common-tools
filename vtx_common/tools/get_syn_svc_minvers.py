import sys
import asyncio
import logging
import argparse
import importlib


logger = logging.getLogger(__name__)

poptsToWords = {
    'ex': 'Example',
    'ro': 'Read Only',
}

info_ignores = (
    'stortype',
    'bases',
    'custom',
)

raw_back_slash_colon = r'\:'

# Make a dummy object
class MockSess:
    def __init__(self):
        self.user = None

class DummyLink:
    def __init__(self):
        self.info = {'sess': MockSess()}

    def get(self, key):
        return self.info.get(key)

class NoValu:
    pass

novalu = NoValu()

# Dyndeps code
def tryDynMod(name):
    '''
    Dynamically import a python module or exception.
    '''
    return importlib.import_module(name)

def tryDynLocal(name):
    '''
    Dynamically import a module and return a module local or raise an exception.
    '''
    if name.find('.') == -1:
        raise ValueError(f'name={name} does not have a period in it.')

    modname, objname = name.rsplit('.', 1)
    mod = tryDynMod(modname)
    item = getattr(mod, objname, novalu)
    if item is novalu:
        raise ValueError(f'No attribute = {objname} in {modname}')
    return item

async def getStormSvcInfo(ctor):
    cls = tryDynLocal(ctor)

    if not hasattr(cls, 'cellapi'):
        raise Exception('ctor must have a cellapi attr')

    cellapi = cls.cellapi

    async with await cellapi.anit(novalu, DummyLink(), novalu) as obj:
        svcinfo = await obj.getStormSvcInfo()

    return svcinfo

def getMessageFromInfo(svcinfo):
    minvers = []
    for pkg in svcinfo.get('pkgs', ()):
        minv = pkg.get('synapse_minversion')
        if minv is None:
            continue
        assert len(minv) == 3
        minvers.append(minv)
    minvers.sort(reverse=True)

    if minvers:
        minv = minvers[0]
        minv = [str(v) for v in minv]
        minv = '.'.join(minv)
        mesg = f'The Storm Service requires a minimum Synapse version of {minv} or greater.'
    else:
        mesg = 'The Storm Service has no minimum Synapse version specified.'
    return mesg

async def main(argv):
    pars = makeargparser()
    opts = pars.parse_args(argv)

    svcinfo = await getStormSvcInfo(opts.ctor)
    mesg = getMessageFromInfo(svcinfo)
    print(mesg)
    return 0

def makeargparser():
    desc = 'Extract a minimum storm service version string.'
    pars = argparse.ArgumentParser('vtx_common.tools.get_syn_svc_minvers', description=desc)

    pars.add_argument('ctor', type=str,
                      help='Storm service ctor')

    return pars


if __name__ == '__main__':  # pragma: no cover
    asyncio.run(main(sys.argv[1:]))

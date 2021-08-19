import asyncio

import vtx_common.tests.common as t_common
import vtx_common.tools.get_syn_svc_minvers as v_gssm

pkg = {
    'name': 'foo',
    'version': (1, 0, 0),
    'synapse_minversion': (2, 48, 0),
    'modules': (
        {
            'name': 'foo',
            'storm': ''
        },
    ),
}

svcinfo = {
    'name': 'foosvc',
    'vers': (1, 0, 2),
    'evts': {},
    'pkgs': [pkg],
}

class MockApi:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.svcinfo = svcinfo

    @classmethod
    async def anit(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        return obj

    async def getStormSvcInfo(self):
        return self.svcinfo

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class MockService:
    cellapi = MockApi

class TestGssm(t_common.TstBase):

    def test_dynload(self):
        ctor = 'vtx_common.tests.test_get_syn_svc_minvers.MockService'
        cls = v_gssm.tryDynLocal(ctor)
        self.true(cls is MockService)

        with self.raises(ValueError):
            ctor = 'vtx_common.tests.test_get_syn_svc_minvers.Newp'
            v_gssm.tryDynLocal(ctor)

        with self.raises(ImportError):
            ctor = 'vtx_common.tests.hahah.Newp'
            v_gssm.tryDynLocal(ctor)

    def test_gssm(self):
        ctor = 'vtx_common.tests.test_get_syn_svc_minvers.MockService'
        coro = v_gssm.getStormSvcInfo(ctor)
        svcinfo = asyncio.run(coro)
        self.len(1, svcinfo.get('pkgs'))

        mesg = v_gssm.getMessageFromInfo(svcinfo)
        self.isin('2.48.0', mesg)

        svcinfo['pkgs'].append({'synapse_minversion': (2, 1, 20)})
        svcinfo['pkgs'].append({'synapse_minversion': (2, 60, 12)})

        mesg = v_gssm.getMessageFromInfo(svcinfo)
        self.isin('2.60.12', mesg)
        self.notin('2.48.0', mesg)

        svcinfo.pop('pkgs', None)
        mesg = v_gssm.getMessageFromInfo(svcinfo)
        self.eq(mesg, 'The Storm Service has no minimum Synapse version specified.')
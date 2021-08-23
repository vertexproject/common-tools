import os
import yaml

import vtx_common.tests.common as t_common
import vtx_common.tools.get_pkg_syn_minver as v_gpsm


def_pkg = {
    'name': 'foo',
    'version': [1, 0, 0],
    'synapse_minversion': [2, 48, 0],
    'modules': [
        {
            'name': 'foo',
            'storm': ''
        },
    ],
}


class TestGpsm(t_common.TstBase):

    def test_gpsm(self):
        with self.getTempdir() as dirn:
            fp = os.path.join(dirn, 'test.yaml')

            with open(fp, 'w') as fd:
                yaml.safe_dump(def_pkg, fd)

            pkg = v_gpsm.yamlload(fp)
            self.eq(pkg, def_pkg)

            mesg = v_gpsm.getMessageFromPkg(pkg, 'Power-Up')
            self.eq(mesg, 'The Power-Up requires a minimum Synapse version of 2.48.0 or greater.')

            pkg.pop('synapse_minversion')
            mesg = v_gpsm.getMessageFromPkg(pkg, 'Power-Up')
            self.eq(mesg, 'The Power-Up has no minimum Synapse version specified.')

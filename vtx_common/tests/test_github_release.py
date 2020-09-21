import os
import argparse

import vtx_common.tests.common as t_common
import vtx_common.tools.github_release as v_ghr


synapse_changelog = '''

v2.7.3 - 2020-09-16
===================

Deprecations
------------

- The ``0.1.x`` to ``2.x.x`` Migration tool and and associated Cortex sync service will be removed from Synapse in
  the ``2.9.0`` release. In order to move forward to ``2.9.0``, please make sure that any Cortexes which still need to
  be migrated will first be migrated to ``2.8.x`` prior to attempting to use ``2.9.x``.
  (`#1880 <https://github.com/vertexproject/synapse/pull/1880>`_)

Bugfixes
--------
- Remove duplicate words in a comment. This was a community contribution from enadjoe.
  (`#1874 <https://github.com/vertexproject/synapse/pull/1874>`_)
- Fix a nested Nexus log event in Storm Service deletion. The ``del`` event causing Storm code execution could lead to
  nested Nexus events, which is incongruent with how Nexus change handlers work. This now spins off the Storm code in
  a free-running coroutine. This does change the service ``del`` semantics since any support Storm packages a service
  had may be removed by the time the handler executes.
  (`#1876 <https://github.com/vertexproject/synapse/pull/1876>`_)
- Fix an issue where the ``cull`` parameter was not being passed to the multiqueue properly when calling ``.gets()``
  on a Storm Types Queue object.
  (`#1876 <https://github.com/vertexproject/synapse/pull/1876>`_)
- Pin the ``nbconvert`` package to a known working version, as ``v6.0.0`` of that package broke the Synapse document
  generation by changing how templates work.
  (`#1876 <https://github.com/vertexproject/synapse/pull/1876>`_)
- Correct ``min`` and ``max`` integer examples in tagprop documentation and tests.
  (`#1878 <https://github.com/vertexproject/synapse/pull/1878>`_)


v2.7.2 - 2020-09-04
===================

Features and Enhancements
-------------------------
- Update tests for additional test code coverage. This was a community contribution from blackout.
  (`#1867 <https://github.com/vertexproject/synapse/pull/1867>`_)
- Add implicit links to documentation generated for Storm services, to allow for direct linking inside of documentation
  to specific Storm commands.
  (`#1866 <https://github.com/vertexproject/synapse/pull/1866>`_)
- Add future support for deprecating model elements in the Synapse data model. This support will produce client and
  server side warnings when deprecated model elements are used or loaded by custom model extensions or CoreModules.
  (`#1863 <https://github.com/vertexproject/synapse/pull/1863>`_)

Bugfixes
--------
- Update ``FixedCache.put()`` to avoid a cache miss. This was a community contribution from blackout.
  (`#1868 <https://github.com/vertexproject/synapse/pull/1868>`_)
- Fix the ioloop construction to be aware of ``SYN_GREEDY_CORO`` environment variable to put the ioloop into debug mode
  and log long-running coroutines.
  (`#1870 <https://github.com/vertexproject/synapse/pull/1870>`_)
- Fix how service permissions are checked in ``$lib.service.get()`` and ``$lib.service.wait()`` Storm library calls.
  These APIs now first check ``service.get.<service iden>`` before checking ``service.get.<service name>`` permissions.
  A successful ``service.get.<service name>`` check will result in a warning to the client and the server.
  (`#1871 <https://github.com/vertexproject/synapse/pull/1871>`_)


v2.7.1 - 2020-08-26
===================

Features and Enhancements
-------------------------
- Refactor an Axon unit test to make it easier to test alternative Axon implementations.
  (`#1862 <https://github.com/vertexproject/synapse/pull/1862>`_)

Bugfixes
--------
- Fix an issue in ``synapse.tools.cmdr`` where it did not ensure that the users Synapse directory was created before
  trying to open files in the directory.
  (`#1860 <https://github.com/vertexproject/synapse/issues/1860>`_)
  (`#1861 <https://github.com/vertexproject/synapse/pull/1861>`_)

Improved Documentation
----------------------
- Fix an incorrect statement in our documentation about the intrinsic Axon that a Cortex creates being remotely
  accessible.
  (`#1862 <https://github.com/vertexproject/synapse/pull/1862>`_)
'''

setup_cfg = '''

[vtx_common:github_release]
release-name = Vertex Common Tools
extra-lines = Words go here

              More words go here!
dry-run = true
remove-urls = false
nope = does not matter
test-int = 1138
'''

extra_lines = '''Words go here

More words go here!'''

class TestGithubRelease(t_common.TstBase):

    def test_changelog(self):

        logs = v_ghr.parse_changelog(synapse_changelog)
        self.eq(3, len(logs))
        self.eq(set(logs.keys()),
                         {'v2.7.1', 'v2.7.2', 'v2.7.3'})

        lines = logs.get('v2.7.1')
        line = '  (`#1860 <https://github.com/vertexproject/synapse/issues/1860>`_)'
        self.true(line in lines)
        line = '- Refactor an Axon unit test to make it easier to test alternative Axon implementations.'
        self.true(line in lines)

        line = '  (`#1880 <https://github.com/vertexproject/synapse/pull/1880>`_)'
        self.false(line in lines)

        nlines = v_ghr.remove_urls(lines)
        line = '  (`#1860 <https://github.com/vertexproject/synapse/issues/1860>`_)'
        self.false(line in nlines)
        line = '- Refactor an Axon unit test to make it easier to test alternative Axon implementations.'
        self.true(line in nlines)

    def test_setup_parse(self):

        v_ghr.CFG_OPTS['test-int'] = {
            'type': 'int',
            'key': 'test_int',
        }
        v_ghr.CFG_OPTS['test-str'] = {
            'type': 'str',
            'key': 'test_str',
            'defval': 'test'
        }

        with self.getTempdir() as dirn:
            fp = os.path.join(dirn, 'temp.cfg')
            with open(fp, 'wb') as fd:
                fd.write(setup_cfg.encode())

            opts = argparse.Namespace()
            self.eq(vars(opts), {})
            v_ghr.pars_config(opts, fp)
            info = vars(opts)

            self.true(len(info) == 6)
            self.eq(info.get('dryrun'), True)
            self.eq(info.get('remove_urls'), False)
            self.eq(info.get('test_int'), 1138)
            self.eq(info.get('release_name'), 'Vertex Common Tools')
            self.eq(info.get('extra_lines'), extra_lines)
            self.eq(info.get('test_str'), 'test')

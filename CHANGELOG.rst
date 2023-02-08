*****************************
Vertex Common Tools Changelog
*****************************

v0.1.20 - 2023-02-08
====================

Features and Enhancements
-------------------------
- Fix wheel builds.

v0.1.19 - 2023-02-08
====================

Features and Enhancements
-------------------------
- Add Python 3.10 support.

v0.1.18 - 2023-01-17
====================

Features and Enhancements
-------------------------
- Add optional mailgun support for emailing raw RST changelogs in the
  ``vtx_common.tools.github_release`` tool.

v0.1.17 - 2022-12-05
====================

Bugfixes
--------
- Update the requirements for ``pytest`, ``pytest-cov`` and ``pytest-xdist``
  in ``setup.py``.

v0.1.16 - 2022-12-01
====================

Features and Enhancements
-------------------------

- Update ``pytest``, ``pytest-cov``, and ``pytest-xdist``
  libraries to be in line with Synapse requirements.

v0.1.15 - 2022-01-17
====================

Features and Enhancements
-------------------------

- Update ``PyYAML``, ``pytest``, ``pytest-cov``, and ``pytest-xdist``
  libraries to be in line with Synapse requirements.


v0.1.14 - 2021-10-14
====================

Features and Enhancements
-------------------------

- Add ``vtx_common.tools.buildpkg`` as a convenience script for building Storm
  packages with rstorm based docs in them. This requires pandoc for execution
  and the synaspe package installed as well.


v0.1.8 - 2021-08-11
===================

Features and Enhancements
-------------------------

- Pin the ``bump2version`` package to ``1.0.1``.


v0.1.6 - 2020-09-21
===================

Features and Enhancements
-------------------------

- Add support for parsing setup.cfg for configuration data that may change often per repository. This release is
  effectively a re-release of v0.1.5 with this changelog entry.
  (`#3 <https://github.com/vertexproject/common-tools/pull/3>`_)


v0.1.4 - 2020-09-17
===================

Final v0.1.4 release.

Features and Enhancements
-------------------------

- Add support for removing urls and adding extra lines to the of a github release.
  (`#2 <https://github.com/vertexproject/common-tools/pull/2>`_)


v0.1.4a1 - 2020-09-17
=====================

Features and Enhancements
-------------------------

- Add support for removing urls and adding extra lines to the of a github release.
  (`#2 <https://github.com/vertexproject/common-tools/pull/2>`_)


v0.1.3 - 2020-09-16
===================

Features and Enhancements
-------------------------

Add a ``--dry-run`` option to the ``github_release`` tool.


Bugfixes
--------

Fix an issue with the README.


v0.1.2 - 2020-09-16
===================

Features and Enhancements
-------------------------

Add the README.rst to the long description for pypi.


v0.1.1 - 2020-09-16
===================

Bugfixes
--------

Moved the pre-commit script since it was not importable.

v0.1.0 - 2020-09-15
===================

Initial public release for the ``vtx_common`` package.


v0.0.1a2 - 2020-09-15
=====================

Re-release with updated url.


v0.0.1a - 2020-09-15
====================

Initial alpha pre-release of a tools rollup.

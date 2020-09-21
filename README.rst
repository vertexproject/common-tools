===================
Vertex Common Tools
===================

A collection of a few common tools which are useful for Python packaging and CI purposes.

These tools can be invoked as Python modules from the Python command line (``python -m <module path>``). Available tools
include the following:

``vtx_common.tools.github_release``
    This can be used to automatically push a Release up to github using a changelog file. Many values may automatically
    be resolved from environment variables. Some values may also come from ``setup.cfg`` files. The following config
    values are read from that location (under the section ``vtx_common:github_release``):

    ``release-name``
        Name to prefix the release as.

    ``extra-lines``
        Additional lines appended to the changelog. This setting may only be set via ``setup.cfg``.

    ``remove-urls``
        Boolean to remove lines starting as RST URL links from changelog lines.

    ``dry-run``
        Do a dry run. Still requires a tag to be parsable from a environment variable.

    ``changelog``
        The changelog file to parse.

``vtx_common.tools.pep8_staged_files``
    Runs ``autopep8`` against the repository. Must be run from the root of the repository. Can use the following Bash
    alias to make this easier to invoke::

        alias pep8staged='python -m vtx_common.tools.pep8_staged_files'

``vtx_common.tools.pre_commit``
    This is used as a Git pre-commit hook. This can be easily installed via the following command::

        echo "python -m vtx_common.tools.pre_commit" > .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

    This will run ``pycodestyle`` against Python files to be committed. It assumes that there is a ``setup.cfg`` file
    in the root directory of the repo.

This package also installs ``bump2version``, ``pytest``, ``pytest-cov`` and ``pytest-xdist`` packages.
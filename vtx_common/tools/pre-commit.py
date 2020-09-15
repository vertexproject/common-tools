#!/usr/bin/env python
"""
Copy this file to .git/hooks/pre-commit in order to have the hooks run when doing a git commit action.

Requires pycodestyle and nbstripout to be installed.

Forked from https://gist.github.com/810399
Updated from https://github.com/cbrueffer/pep8-git-hook
"""
from __future__ import print_function
import os
import shutil
import sys
import tempfile

import vtx_common.utils as v_utils

def main():
    lint_python()

def lint_python():
    gitdir = v_utils.system('git', 'rev-parse', '--show-toplevel').decode('utf-8').strip()
    files = v_utils.system('git', 'diff', '--cached', '--name-only').decode('utf-8')
    pyfiles = [file.strip() for file in files.split('\n') if file.strip().endswith('.py')]

    if pyfiles:
        print('pre-commit - running pycodestyle against python files.')
        tempdir = tempfile.mkdtemp()
        for name in pyfiles:
            filename = os.path.join(tempdir, name)
            filepath = os.path.dirname(filename)

            if not os.path.exists(filepath):
                os.makedirs(filepath)
            with open(filename, 'w') as f:
                v_utils.system('git', 'show', ':' + name, stdout=f)

        args = ['pycodestyle', f'--config={gitdir}/setup.cfg']
        args.append('.')
        output = v_utils.system(*args, cwd=tempdir)
        shutil.rmtree(tempdir)
        if output:
            print('PEP8 style violations have been detected.  Please fix them\n'
                  'or force the commit with "git commit --no-verify".\n')
            print(output.decode('utf-8'),)
            sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()

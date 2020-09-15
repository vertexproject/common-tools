#!/usr/bin/env python
#
# Requires autopep8 to be installed.
# Script for cleaning up most PEP8 related errors checked by the pre-commit hook.
#
import os
import sys

import vtx_common.utils as v_utils

def main():
    cwd = os.getcwd()
    if not v_utils.reqGitDir(cwd):
        print('Must be run from the root of the repository.')
        sys.exit(1)
    files = v_utils.system('git', 'diff', '--cached', '--name-only').decode("utf-8")
    files = [file.strip() for file in files.split('\n') if file.strip().endswith('.py')]

    if not files:
        sys.exit(0)

    args = ['autopep8', '--in-place']

    args.extend(files)
    output = v_utils.system(*args, cwd=cwd)
    if output:
        print(output.decode("utf-8"),)
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()

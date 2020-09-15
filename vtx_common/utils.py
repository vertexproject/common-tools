import os
import subprocess


from typing import ByteString, AnyStr

def system(*args, **kwargs) -> ByteString:
    '''Simple subprocess wrapper'''
    kwargs.setdefault('stdout', subprocess.PIPE)
    proc = subprocess.Popen(args, **kwargs)
    out, err = proc.communicate()
    return out

def reqGitDir(cwd: AnyStr =None) -> bool:
    if not cwd:
        cwd = os.getcwd()
    gitdir = os.path.join(cwd, '.git')
    if os.path.isdir(gitdir):
        return True
    return False

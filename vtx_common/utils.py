import os
import logging
import subprocess

import requests

from typing import List, AnyStr

logger = logging.getLogger(__name__)

def system(*args, **kwargs) -> bytes:
    '''Simple subprocess wrapper'''
    kwargs.setdefault('stdout', subprocess.PIPE)
    proc = subprocess.Popen(args, **kwargs)
    out, err = proc.communicate()
    return out

def reqGitDir(cwd: AnyStr =None) -> bool:
    '''Require the given directory to have a .git directory in it.'''
    if not cwd:
        cwd = os.getcwd()
    gitdir = os.path.join(cwd, '.git')
    if os.path.isdir(gitdir):
        return True
    return False

def sendMailMessage(dest: List[AnyStr],
                    sender: AnyStr,
                    text: AnyStr,
                    subject: AnyStr,
                    domain: AnyStr,
                    token=AnyStr) -> bool:
    url = f'https://api.mailgun.net/v3/{domain}/messages'
    payload = {
        'from': sender,
        'to': ','.join(dest),
        'subject': subject,
        'text': text,
    }
    auth = requests.auth.HTTPBasicAuth('api', token)
    resp = requests.post(url, auth=auth, data=payload)
    if resp.status_code != 200:
        logger.error(f'Failed to send email: {resp}')
        return False
    logger.info('Sent email :)')
    return True

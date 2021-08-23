import re
import os
import sys
import logging
import argparse
import collections
import configparser

from typing import List, AnyStr

import github

import vtx_common.tools.get_pkg_syn_minver as v_gpsm


HEADER_RE = r'v[0-9]+\.[0-9]+\.[0-9]+((a|b|rc)[0-9]*)?\s-\s20[0-9]{2}-[0-9]{2}-[0-9]{2}'
PASSLINE = r'^=.*$'
SEMVER_RE = r'v[0-9]+\.[0-9]+\.[0-9]+(?P<pre>((a|b|rc)[0-9]*)?)'
URL_RE = r'\s+\(`#\d+\s<http'
logger = logging.getLogger(__name__)

CFG_HEADER = 'vtx_common:github_release'

DRYRUN = 'dryrun'
CHANGELOG = 'changelog'
CHANGELOG_PKGNAME = 'changelog_pkgname'
REMOVE_URLS = 'remove_urls'
RELEASE_NAME = 'release_name'
STORM_PKG_FILE = 'storm_pkg_file'
STORM_PKG_TYPE = 'storm_pkg_type'
STORM_PKG_FILE_PKGNAME = 'storm_pkg_file_pkgname'

CFG_OPTS = {
    'release-name': {
        'type': 'str',
        'key': RELEASE_NAME,
    },
    'extra-lines': {
        'type': 'str',
        'key': 'extra_lines',
        'defval': ''
    },
    'remove-urls': {
        'type': 'bool',
        'key': REMOVE_URLS,
    },
    'dry-run': {
        'type': 'bool',
        'key': DRYRUN,
    },
    'storm-pkg-file': {
        'type': 'str',
        'key': STORM_PKG_FILE,
    },
    'storm-pkg-file-pkgname': {
        'type': 'bool',
        'key': STORM_PKG_FILE_PKGNAME,
    },
    'storm-pkg-type': {
        'type': 'str',
        'key': STORM_PKG_TYPE,
    },
    'changelog': {
        'type': 'str',
        'key': CHANGELOG,
    },
    'changelog-pkgname': {
        'type': 'bool',
        'key': CHANGELOG_PKGNAME,
    },
}

def get_parser():
    pars = argparse.ArgumentParser()
    pars.add_argument('-g', '--github-token', dest='gittokenvar', default='GITHUB_TOKEN', type=str,
                      help='Environment variable to pull the github token from.')
    pars.add_argument('-u', '--github-user', dest='gituservar', default='CIRCLE_PROJECT_USERNAME', type=str,
                      help='Environment variable to pull the github user from')
    pars.add_argument('-r', '--github-repo', dest='gitrepovar', default='CIRCLE_PROJECT_REPONAME', type=str,
                      help='Environment variable to pull the github repo from')
    pars.add_argument('-t', '--tagvar', dest='tagvar', default='CIRCLE_TAG', type=str,
                      help='Environment variable to pull the tag from.')
    pars.add_argument('-c', '--changelog', dest=CHANGELOG, default='./CHANGELOG.rst',
                      help='Path to changelog file to process')
    pars.add_argument('--changelog-pkgname', dest=CHANGELOG_PKGNAME, default=False, action='store_true',
                      help='inject package name derived from a tag into the changelog path.')
    pars.add_argument('--remove-urls', dest=REMOVE_URLS, default=False, action='store_true',
                      help='Remove lines starting with RST formated links.')
    pars.add_argument('-d', '--dry-run', dest=DRYRUN, default=False, action='store_true',
                      help='Do not do an actual Github release action. Does not require github variables to be set.'
                           'Does require the tag variable to be set. This will print the changlog found to stderr.')
    pars.add_argument('--release-name', dest=RELEASE_NAME, default=None, type=str,
                      help='Release name to prefix the tag with for the github release.')
    pars.add_argument('--pkg-file', dest=STORM_PKG_FILE, default=None, type=str,
                      help='Storm package file to get minimum storm service from.')
    pars.add_argument('--pkg-file-inject', dest=STORM_PKG_FILE_PKGNAME, default=False, action='store_true',
                      help='inject pkgname derived from a tag into the pkgapath path')
    pars.add_argument('--pkg-type', dest=STORM_PKG_TYPE, default=None, type=str, choices=['Storm Service', 'Power-Up'],
                      help='Storm package file to get minimum storm service from.')

    return pars

def parse_changelog(s: str) -> dict:
    curv = None
    ret = collections.defaultdict(list)
    for line in s.split('\n'):
        if re.match(HEADER_RE, line):
            curv = line.split(' ', 1)[0]
            continue
        if re.match(PASSLINE, line):
            continue
        if curv:
            ret[curv].append(line)

    return ret

def remove_urls(lines: List[AnyStr]) -> List[AnyStr]:
    ret = []
    for line in lines:
        if re.search(URL_RE, line):
            continue
        ret.append(line)
    return ret

def pars_config(opts: argparse.Namespace,
                fn: AnyStr,
                ):
    if not os.path.exists(fn):
        logger.debug('Config file [{}] does not exist.')
        return

    config = configparser.RawConfigParser()
    config.read(fn)

    if not config.has_section(CFG_HEADER):
        logger.info(f'No {CFG_HEADER} header found')

    for opt, info in CFG_OPTS.items():
        typ = info.get('type')
        defval = info.get('defval')
        try:
            if typ == 'bool':
                valu = config.getboolean(CFG_HEADER, opt)
            elif typ == 'int':
                valu = config.getint(CFG_HEADER, opt)
            else:
                valu = config.get(CFG_HEADER, opt,)
        except (configparser.NoOptionError, configparser.NoSectionError):
            if defval is None:
                continue
            valu = defval

        setattr(opts, info.get('key'), valu)

    logger.info(f'Parsed {opts} from setup.cfg')
    return

def main(argv):
    pars = get_parser()

    opts = argparse.Namespace()
    pars_config(opts, 'setup.cfg')

    opts = pars.parse_args(argv, namespace=opts)
    logger.info(f'Final namespace: {opts}')

    tag = os.getenv(opts.tagvar, '')
    if not tag:
        logger.error(f'No tag found for {opts.tagvar}')
        return 1

    logger.info(f'envar {opts.tagvar} resolved to {tag}')
    nicetag = tag
    pkgname = None
    if '@' in tag:
        logger.info('@ delimited tag, splitting into name and tag part')
        pkgname, nicetag = tag.split('@')
        logger.info(f'Got pkgname={pkgname} @ nicetag={nicetag}')
    m = re.search(SEMVER_RE, nicetag)
    if not m:
        logger.error(f'nicetag={nicetag} does not match semver regex')
        return 1
    is_prerelease = False
    if m.groupdict().get('pre'):
        is_prerelease = True

    defvalu = ''
    if opts.dryrun:
        defvalu = 'DRYRUN'

    gh_token = os.getenv(opts.gittokenvar, defvalu)
    if not gh_token:
        logger.error('No github token found')
        return 1
    gh_username = os.getenv(opts.gituservar, defvalu)
    if not gh_username:
        logger.error('No github user found')
        return 1
    gh_repo = os.getenv(opts.gitrepovar, defvalu)
    if not gh_repo:
        logger.error('No github repo found')
        return 1

    extra_parts = []

    pfile = opts.storm_pkg_file
    mtyp = opts.storm_pkg_type
    if pfile and mtyp:

        if opts.storm_pkg_file_pkgname:
            assert pkgname is not None
            logger.info('Injecting pkgname to pkg path')
            pfile = pfile.format(pkgname=pkgname)

        logger.info(f'Getting storm package from {pfile}')
        pkg = v_gpsm.yamlload(pfile)
        minv_message = v_gpsm.getMessageFromPkg(pkg, mtyp)
        logger.info(f'Got message: {minv_message}')
        extra_parts.append(minv_message)

    extra_lines = opts.extra_lines
    if extra_lines:
        logger.info(f'Extra lines found: {extra_lines}')
        extra_parts.append(extra_lines)

    # Join extra lines together
    extra_lines = '\n'.join(extra_parts)

    changelog_fp = opts.changelog
    if opts.changelog_pkgname:
        assert pkgname is not None
        logger.info('Injecting pkgname to changelog path')
        changelog_fp = changelog_fp.format(pkgname=pkgname)

    assert os.path.isfile(changelog_fp)
    raw_changelog = open(changelog_fp, 'rb').read().decode()
    parsed_logs = parse_changelog(raw_changelog)

    target_log = parsed_logs.get(nicetag)
    if not target_log:
        logger.error(f'Unable to find logs for tag [{nicetag}]')
        # It's possible for pre-release tags to end up without a changelog.
        # This condition should not end up failing a CI pipeline.
        return 0
    logger.info(f'Found changelogs for [{nicetag}] in [{opts.changelog}]')

    if opts.remove_urls:
        logger.info('Removing URLs')
        target_log = remove_urls(target_log)

    # join logs together and strip them
    target_log = '\n'.join(target_log)
    target_log = target_log.strip()

    if extra_lines:
        logger.info(f'Appending extra line data')
        target_log = '\n'.join([target_log, '', extra_lines])
        # remove trailing data if present in extra_lines
        target_log = target_log.strip()

    logger.info('Final Log:')
    for line in target_log.split('\n'):
        logger.debug(line)

    name = tag
    if opts.release_name:
        name = f'{opts.release_name} {tag}'

    logger.info(f'Release Name: [{name}]')
    gh_repo_path = f'{gh_username}/{gh_repo}'

    if opts.dryrun:
        logger.info('Dry-run mode enabled. Not performing a Github release action.')
        logger.info('Would have made release with the following information:')
        logger.info(f'gh_repo_path={gh_repo_path}')
        logger.info(f'tag={tag}')
        logger.info(f'name={name}')
        logger.info(f'prerelease={is_prerelease}')
        logger.info(f'message={target_log}')
        return 0

    gh = github.Github(gh_token)

    logger.info(f'Getting github repo for {gh_repo_path}')
    repo = gh.get_repo(gh_repo_path)

    logger.info('Making github release')
    release = repo.create_git_release(tag=tag,
                                      name=name,
                                      draft=False,
                                      message=target_log,
                                      prerelease=is_prerelease,
                                      )
    logger.info(f'Made github release {release}')

    return 0

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main(sys.argv[1:]))

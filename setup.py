#!/usr/bin/env python
import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install

VERSION = '0.2.0'

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG', '')
        tag = tag.lstrip('v')

        if tag != VERSION:
            info = f"Git tag: {tag} does not match the version of this app: {VERSION}"
            sys.exit(info)

long_description_content_type = None
long_description = None
readme = './README.rst'
if os.path.exists(readme):

    print(f'Adding {readme} contents as the long description.')

    with open('./README.rst', 'rb') as fd:
        buf = fd.read()
    long_description = buf.decode()
    long_description_content_type = 'text/x-rst'


setup(
    name='vtx-common',
    version=VERSION,
    description='Vertex project tools to assist with packaging.',
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    author='The Vertex Project LLC',
    author_email='epiphyte+tools@vertex.link',
    url='https://github.com/vertexproject/common-tools',
    license='Apache License 2.0',

    packages=find_packages(exclude=['scripts',
                                    ]),

    include_package_data=True,
    python_requires='>=3.11',
    install_requires=[
        'PyGithub==1.53',
        'PyYAML',
        'bump2version>=1.0.1,<2.0.0',
        'pytest',
        'autopep8',
        'pytest-cov',
        'pycodestyle',
        'pytest-xdist',
    ],
    extras_require={
        'synapse': [
            'synapse>=2.115.1,<3.0.0',
        ]
    },

    classifiers=[
        'Development Status :: 4 - Beta',

        'License :: OSI Approved :: Apache Software License',

        'Topic :: System :: Clustering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Software Distribution',

        'Programming Language :: Python :: 3.11',
    ],
    cmdclass={
        'verify': VerifyVersionCommand,
    },
)

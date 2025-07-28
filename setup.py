# Copyright (c) 2014-2024  Barnstormer Softworks, Ltd.
# Copyright (c) 2025  Kent State University CAE-Netlab

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup, find_packages

import os
import os.path
import platform

requires = ["cryptography",
            "ipaddress",
            "lxml",
            "requests",
            "six",
            "wrapt"]

pkgs = find_packages()
pkgs.append('')

setup(name = 'geni-lib',
      version = '1.0.0',
      author = 'Nick Bastin',
      author_email = 'nbastin@protonmail.com',
      description = 'Library and tools for working with research testbed resources that support ' \
                    'the GENI AM API, including the NSF GENI Testbed (www.geni.net) and Cloudlab (cloudlab.us).',
      long_description = open("README.rst", "r").read(),
      packages = pkgs,
      package_dir = {'geni' : 'geni', 'ccloud' : 'ccloud'},
      pymodules = ['genish'],
      scripts = ['tools/buildcontext/context-from-bundle',
                 'tools/buildcontext/build-context',
                 'tools/shell/genish'],

      install_requires = requires,
      classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        ]
      )

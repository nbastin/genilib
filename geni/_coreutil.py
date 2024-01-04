# Copyright (c) 2015-2020  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import os
import os.path
import ssl

import pkg_resources

WIN32_ATTR_HIDDEN = 0x02
VERSION = pkg_resources.require("geni-lib")[0].version

def getDefaultDir ():
  HOME = os.path.expanduser("~")

  if os.name == "posix":
    DEF_DIR = "%s/.bssw/geni/" % (HOME)
    if not os.path.exists(DEF_DIR):
      os.makedirs(DEF_DIR, 0o775)
  elif os.name == "nt":
    DEF_DIR = "%s/bssw/geni/" % (HOME)
    if not os.path.exists(DEF_DIR):
      os.makedirs(DEF_DIR, 0o775)
      import ctypes
      BSSW = "%s/bssw" % (HOME)
      if not ctypes.windll.kernel32.SetFileAttributesW(unicode(BSSW), WIN32_ATTR_HIDDEN):
        raise ctypes.WinError()

  return DEF_DIR

def getDefaultAggregatePath():
  ddir = getDefaultDir()
  return "%s/aggregates.json" % (ddir)

def getOSName ():
  if os.name == "posix":
    return "%s-%s" % (os.uname()[0], os.uname()[4])
  elif os.name == "nt":
    import platform
    return "%s-%s" % (platform.platform(), platform.architecture()[0])
  return "unknown"


def defaultHeaders ():
  d = {"User-Agent" : "GENI-LIB %s (%s)" % (VERSION, getOSName())}
  return d

def getDefaultContextPath ():
  ddir = getDefaultDir()
  return os.path.normpath("%s/context.json" % (ddir))

def disableUrllibWarnings ():
  try:
    import requests.packages.urllib3
    import requests.packages.urllib3.exceptions

    warnings = []
    try:
      warnings.append(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    except AttributeError:
      pass

    try:
      warnings.append(requests.packages.urllib3.exceptions.InsecurePlatformWarning)
    except AttributeError:
      pass

    try:
      warnings.append(requests.packages.urllib3.exceptions.SNIMissingWarning)
    except AttributeError:
      pass

    requests.packages.urllib3.disable_warnings(tuple(warnings))
  except ImportError:
    # This version of requests doesn't have urllib3 in it
    return

# pylint: disable=cyclic-import
def shellImports ():
  imports = {}

  import geni.constants
  import geni.util
  import geni.rspec.pg
  import geni.rspec.vts
  import geni.rspec.igext
  import geni.rspec.egext
  import geni.rspec.igutil
  import geni.aggregate.frameworks
  import geni.aggregate.instageni
  import geni.aggregate.vts
  import geni.aggregate.exogeni
  import geni.aggregate.cloudlab
  import geni.aggregate.transit
  import pprint

  imports["util"] = geni.util
  imports["PG"] = geni.rspec.pg
  imports["VTS"] = geni.rspec.vts
  imports["IGAM"] = geni.aggregate.instageni
  imports["VTSAM"] = geni.aggregate.vts
  imports["EGAM"] = geni.aggregate.exogeni
  imports["CLAM"] = geni.aggregate.cloudlab
  imports["TRANSITAM"] = geni.aggregate.transit
  imports["IGX"] = geni.rspec.igext
  imports["EGX"] = geni.rspec.egext
  imports["IGUtil"] = geni.rspec.igutil
  imports["PP"] = pprint.pprint
  imports["RegM"] = geni.aggregate.frameworks.MemberRegistry
  imports["SLICE_ROLE"] = geni.constants.SLICE_ROLE
  imports["PROJECT_ROLE"] = geni.constants.PROJECT_ROLE
  imports["REQSTATUS"] = geni.constants.REQSTATUS

  return imports


# pylint: disable=wrong-import-position
from requests.adapters import HTTPAdapter
try:
  from requests.packages.urllib3.poolmanager import PoolManager
  class TLSHttpAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
      self.poolmanager = PoolManager(num_pools = connections, maxsize = maxsize,
                                     block = block, ssl_version = ssl.PROTOCOL_TLS)
except ImportError:
  TLSHttpAdapter = HTTPAdapter

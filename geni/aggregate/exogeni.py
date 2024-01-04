# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import inspect
import sys

from .core import AM

class EGCompute(AM):
  def __init__ (self, name, host, cmid = None, url = None):
    if url is None:
      url = "https://%s:11443/orca/xmlrpc" % (host)
    super(EGCompute, self).__init__(name, url, "amapiv2", "exogeni", cmid)

EXOSM = EGCompute("exosm", "geni.renci.org")
GPO = EGCompute("eg-gpo", "bbn-hn.exogeni.net")
RCI = EGCompute("eg-rci", "rci-hn.exogeni.net")
FIU = EGCompute("eg-fiu", "fiu-hn.exogeni.net")
UH = EGCompute("eg-uh", "uh-hn.exogeni.net")
NCSU = EGCompute("eg-ncsu", "ncsu-hn.exogeni.net")
UFL = EGCompute("eg-ufl", "ufl-hn.exogeni.net")
OSF = EGCompute("eg-osf", "osf-hn.exogeni.net")
NICTA = EGCompute("eg-nicta", "nicta-hn.exogeni.net")
SL = EGCompute("eg-sl", "sl-hn.exogeni.net")
TAMU = EGCompute("eg-tamu", "tamu-hn.exogeni.net")
WVN = EGCompute("eg-wvn", "wvn-hn.exogeni.net")
WSU = EGCompute("eg-wsu", "wsu-hn.exogeni.net")

def aggregates ():
  module = sys.modules[__name__]
  for _,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      yield obj

def name_to_aggregate ():
  result = dict()
  module = sys.modules[__name__]
  for _,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      result[obj.name] = obj
  return result

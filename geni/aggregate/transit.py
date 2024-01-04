# Copyright (c) 2014-2015  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import inspect
import sys

from .core import AM

class Transit(AM):
  def __init__ (self, name, amtype, cmid, url):
    super(Transit, self).__init__(name, url, "amapiv2", amtype, cmid)


AL2S = Transit("i2-al2s", "oess", "urn:publicid:IDN+al2s.internet2.edu+authority+am",
               "https://geni-al2s.net.internet2.edu:3626/foam/gapi/2")

ION = Transit("i2-ion", "pg", "urn:publicid:IDN+ion.internet2.edu+authority+am",
              "http://geni-am.net.internet2.edu:12346")

MAX = Transit("dcn-max", "pg", "urn:publicid:IDN+dragon.maxgigapop.net+authority+am",
              "http://max-myplc.dragon.maxgigapop.net:12346")

Utah = Transit("utah-stitch", "pg", "urn:publicid:IDN+stitch.geniracks.net+authority+cm",
               "https://stitch.geniracks.net:12369/protogeni/xmlrpc/am")

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

# Copyright (c) 2013-2015  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import inspect
import sys

from .core import AM

class OGCompute(AM):
  def __init__ (self, name, host, cmid = None, url = None):
    if url is None:
      url = "https://%s:5002" % (host)
    super(OGCompute, self).__init__(name, url, "amapiv2", "opengeni", cmid)

GPO_OG = OGCompute("gpo-og", "bbn-cam-ctrl-1.gpolab.bbn.com", "urn:publicid:IDN+bbn-cam-ctrl-1.gpolab.bbn.com+authority+am")
CLEMSON_OG = OGCompute("clemson-og", "clemson-clemson-control-1.clemson.edu",
                       "urn:publicid:IDN+clemson-clemson-control-1.clemson.edu+authority+am")
UKL_OG = OGCompute("ukl-og", "glab077.e4.ukl.german-lab.de", "urn:publicid:IDN+glab077.e4.ukl.german-lab.de:gcf+authority+am")

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

# Copyright (c) 2013-2017  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import inspect
import sys

from .protogeni import PGCompute

class IGCompute(PGCompute): pass

# TODO: Should warn if CMID from advertisement differs from one here

CaseWestern = IGCompute("ig-cwru", "boss.geni.case.edu", "urn:publicid:IDN+geni.case.edu+authority+cm")
CENIC = IGCompute("ig-cenic", "instageni.cenic.net", "urn:publicid:IDN+instageni.cenic.net+authority+cm")
Cornell = IGCompute("ig-cornell", "geni.it.cornell.edu", "urn:publicid:IDN+geni.it.cornell.edu+authority+cm")
Chicago = IGCompute("ig-chicago", "geni.uchicago.edu", "urn:publicid:IDN+geni.uchicago.edu+authority+cm")
Clemson = IGCompute("ig-clemson", "instageni.clemson.edu", "urn:publicid:IDN+instageni.clemson.edu+authority+cm")
Colorado = IGCompute("ig-colorado", "instageni.colorado.edu", "urn:publicid:IDN+instageni.colorado.edu+authority+cm")
Dublin = IGCompute("ig-ohmetrodc", "instageni.metrodatacenter.com", "urn:publicid:IDN+instageni.metrodatacenter.com+authority+cm")
GATech = IGCompute("ig-gatech", "instageni.rnoc.gatech.edu", "urn:publicid:IDN+instageni.rnoc.gatech.edu+authority+cm")
GPO = IGCompute("ig-gpo", "boss.instageni.gpolab.bbn.com", "urn:publicid:IDN+instageni.gpolab.bbn.com+authority+cm")
Illinois = IGCompute("ig-illinois", "instageni.illinois.edu", "urn:publicid:IDN+instageni.illinois.edu+authority+cm")
Kansas = IGCompute("ig-kansas", "instageni.ku.gpeni.net", "urn:publicid:IDN+instageni.ku.gpeni.net+authority+cm")
Kentucky = IGCompute("ig-kentucky", "boss.lan.sdn.uky.edu", "urn:publicid:IDN+lan.sdn.uky.edu+authority+cm")
Kettering = IGCompute("ig-kettering", "geni.kettering.edu", "urn:publicid:IDN+geni.kettering.edu+authority+cm")
LSU = IGCompute("ig-lsu", "instageni.lsu.edu", "urn:publicid:IDN+instageni.lsu.edu+authority+cm")
MAX = IGCompute("ig-max", "instageni.maxgigapop.net", "urn:publicid:IDN+instageni.maxgigapop.net+authority+cm")
Missouri = IGCompute("ig-missouri", "instageni.rnet.missouri.edu", "urn:publicid:IDN+instageni.rnet.missouri.edu+authority+cm")
MOXI = IGCompute("ig-moxi", "instageni.iu.edu", "urn:publicid:IDN+instageni.iu.edu+authority+cm")
Northwestern = IGCompute("ig-northwestern", "instageni.northwestern.edu",
                         "urn:publicid:IDN+instageni.northwestern.edu+authority+cm")
NPS = IGCompute("ig-nps", "instageni.nps.edu", "urn:publicid:IDN+instageni.nps.edu+authority+cm")
NYSERNet = IGCompute("ig-nysernet", "instageni.nysernet.org", "urn:publicid:IDN+instageni.nysernet.org+authority+cm")
NYU = IGCompute("ig-nyu", "genirack.nyu.edu", "urn:publicid:IDN+genirack.nyu.edu+authority+cm")
Princeton = IGCompute("ig-princeton", "instageni.cs.princeton.edu", "urn:publicid:IDN+instageni.cs.princeton.edu+authority+cm")
Rutgers = IGCompute("ig-rutgers", "instageni.rutgers.edu", "urn:publicid:IDN+instageni.rutgers.edu+authority+cm")
SOX = IGCompute("ig-sox", "instageni.sox.net", "urn:publicid:IDN+instageni.sox.net+authority+cm")
Stanford = IGCompute("ig-stanford", "instageni.stanford.edu", "urn:publicid:IDN+instageni.stanford.edu+authority+cm")
UCLA = IGCompute("ig-ucla", "instageni.idre.ucla.edu", "urn:publicid:IDN+instageni.idre.ucla.edu+authority+cm")
UKYMCV = IGCompute('ig-ukymcv', 'mcv.sdn.uky.edu', 'urn:publicid:IDN+mcv.sdn.uky.edu+authority+cm')
UKYPKS2 = IGCompute('ig-ukypks2', 'pks2.sdn.uky.edu', 'urn:publicid:IDN+pks2.sdn.uky.edu+authority+cm')
UMichigan = IGCompute('ig-umich', 'instageni.research.umich.edu', 'urn:publicid:IDN+instageni.research.umich.edu+authority+cm')
UMKC = IGCompute('ig-umkc', 'instageni.umkc.edu', 'urn:publicid:IDN+instageni.umkc.edu+authority+cm')
Utah = IGCompute("ig-utah", "boss.utah.geniracks.net", "urn:publicid:IDN+utah.geniracks.net+authority+cm")
UtahDDC = IGCompute("ig-utahddc", "boss.utahddc.geniracks.net", "urn:publicid:IDN+utahddc.geniracks.net+authority+cm")
UTC = IGCompute("ig-utc", "instageni.utc.edu", "urn:publicid:IDN+instageni.utc.edu+authority+cm")
UWashington = IGCompute("ig-uwashington", "instageni.washington.edu", "urn:publicid:IDN+instageni.washington.edu+authority+cm")
Wisconsin = IGCompute("ig-wisconsin", "instageni.wisc.edu", "urn:publicid:IDN+instageni.wisc.edu+authority+cm")
UKYMCV = IGCompute('ig-ukymcv', 'mcv.sdn.uky.edu', 'urn:publicid:IDN+mcv.sdn.uky.edu+authority+cm')

def aggregates ():
  module = sys.modules[__name__]
  for _,obj in inspect.getmembers(module):
    if isinstance(obj, PGCompute):
      yield obj

def name_to_aggregate ():
  result = dict()
  module = sys.modules[__name__]
  for _,obj in inspect.getmembers(module):
    if isinstance(obj, PGCompute):
      result[obj.name] = obj
  return result

def cmid_to_aggregate ():
  result = dict()
  module = sys.modules[__name__]
  for _,obj in inspect.getmembers(module):
    if isinstance(obj, PGCompute):
      result[obj._cmid] = obj
  return result

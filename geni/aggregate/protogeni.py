# Copyright (c) 2013-2017  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import inspect
import sys

from .core import AM, APIRegistry

class PGCompute(AM):
  def __init__ (self, name, host, cmid = None, url = None):
    if url is None:
      url = "https://%s:12369/protogeni/xmlrpc/am/2.0" % (host)
    self.urlv3 = "%s3.0" % (url[:-3])
    self._apiv3 = APIRegistry.get("amapiv3")
    super(PGCompute, self).__init__(name, url, "amapiv2", "pg", cmid)

  def geniRestart (self, context, sname, urns):
    if not isinstance(urns, list):
      urns = [urns]
    return self._apiv3.poa(context, self.urlv3, sname, "geni_restart", urns)

  def geniStart (self, context, sname):
    return self._apiv3.poa(context, self.urlv3, sname, "geni_start")

  def geniUpdateUsers (self, context, sname, user_info_list):
    # user_info_list:
    # [ { "urn" : <str>, "keys" : [ <str>, ...] }, ... ]
    return self._apiv3.poa(context, self.urlv3, sname, "geni_update_users", options = {"geni_users" : user_info_list})

  def geniCancelUpdateUsers (self, context, sname):
    return self._apiv3.poa(context, self.urlv3, sname, "geni_updating_users_cancel")

  def getConsoleURL (self, context, sname, urn):
    return self._apiv3.poa(context, self.urlv3, sname, "geni_console_url", urns = [urn])


Kentucky_PG = PGCompute('pg-kentucky', 'www.uky.emulab.net', 'urn:publicid:IDN+uky.emulab.net+authority+cm')
UTAH_PG = PGCompute('pg-utah', 'www.emulab.net', 'urn:publicid:IDN+emulab.net+authority+cm')
Wall2_PG = PGCompute("pg-wall2", "www.wall2.ilabt.iminds.be", "urn:publicid:IDN+wall2.ilabt.iminds.be+authority+cm")
Wall1_PG = PGCompute("pg-wall1", "www.wall1.ilabt.iminds.be", "urn:publicid:IDN+wall1.ilabt.iminds.be+authority+cm")
wilab_PG = PGCompute("pg-wilab", "www.wilab2.ilabt.iminds.be", "urn:publicid:IDN+wilab2.ilabt.iminds.be+authority+cm")

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

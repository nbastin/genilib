# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import requests

from . import germ

class Admin(object):
  URL = "https://%s:%d/core/admin/%s"

  def __init__ (self, connection):
    self._conn = connection

  @property
  def configkeys (self):
    url = Admin.URL % (self._conn.host, self._conn.port, "get-config-keys")
    r = requests.get(url, **self._conn.rkwargs)
    return r.json()["value"]

  @property
  def version (self):
    url = Admin.URL % (self._conn.host, self._conn.port, "get-version")
    r = requests.get(url, **self._conn.rkwargs)
    return r.json()["value"]["version"]

  def getConfig (self, key):
    url = Admin.URL % (self._conn.host, self._conn.port, "get-config")
    d = json.dumps({"key":key})
    r = requests.post(url, d, **self._conn.rkwargs)
    return r.json()["value"]

class GENI(object):
  URL = "https://%s:%d/core/admin/%s"

  def __init__ (self, connection):
    self._c = connection

  @property
  def slivers (self):
    url = GENI.URL % (self._c.host, self._c.port, "list-slivers")
    r = requests.get(url, **self._c.rkwargs)
    d = r.json()
    if d["retcode"] != 0:
      return None #TODO Raise exception
    sl = []
    # TODO: Make a real sliver object that can lazily get back to type-specific data
    for sliver in d["value"]["slivers"]:
      sl.append(sliver)
    return sl


class Connection(germ.Connection):
  def __init__ (self):
    super(Connection, self).__init__()
    self.user = "foamadmin"
    self.admin = Admin(self)
    self.geni = GENI(self)

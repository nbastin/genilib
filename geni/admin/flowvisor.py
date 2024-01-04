# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import xmlrpclib

class Connection(object):
  def __init__ (self):
    self.user = "fvadmin"
    self.password = None
    self.host = "localhost"
    self.jsonport = 8081
    self.xmlrpcport = 8080

    self._xmlconn = None
    self._jsonconn = None

  @property
  def xmlconn (self):
    if self._xmlconn is None:
      self._xmlconn = xmlrpclib.ServerProxy("https://%s:%s@%s:%d/xmlrpc" % (
        self.user, self.password, self.host, self.xmlrpcport))
    return self._xmlconn

  def getVersion (self):
    s = self.xmlconn.api.ping("foo")
    ver = s.split("=")[1].split(":")[0].split("-")[1]
    return ver

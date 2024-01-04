# Copyright (c) 2017  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

class AMTYPE(object):
  FOAM = "foam"
  VTS = "vts"
  IG = "ig"
  PG = "ig"
  EG = "eg"
  OTHER = "other"

class AMSpec(object):
  def __init__ (self):
    self.cmid = None
    self.desc = None
    self.shortname = None
    self.longname = None
    self.url = None
    self.type = None
    self.cert = None

  def __json__ (self):
    d = {"version" : 1,
         "cmid" : self.cmid,
         "desc" : self.desc,
         "longname" : self.longname,
         "shortname" : self.shortname,
         "url" : self.url,
         "type" : self.type,
         "cert" : self.cert}
    return d

  @classmethod
  def _jconstruct (cls, obj):
    ams = cls()
    ams.cmid = obj["cmid"]
    ams.desc = obj["desc"]
    ams.shortname = obj["shortname"]
    ams.longname = obj["longname"]
    ams.url = obj["url"]
    ams.type = obj["type"]
    ams.cert = obj["cert"]
    return ams

  def build (self):
    am = None
    if self.type == AMTYPE.IG:
      from .instageni import IGCompute
      am = IGCompute(self.shortname, None, self.cmid, self.url)
      am.cert_data = self.cert
    elif self.type == AMTYPE.EG:
      from .exogeni import EGCompute
      am = EGCompute(self.shortname, None, self.cmid, self.url)
      am.cert_data = self.cert
    elif self.type == AMTYPE.VTS:
      from .vts import VTS
      am = VTS(self.shortname, None, self.url)
      am.cert_data = self.cert
    if am:
      am._amspec = self
    return am


# Emulab GID PEM data often lacks begin/end markers
def fixCert (data):
  if data[0:3] != "---":
    data = "-----BEGIN CERTIFICATE-----\n%s\n-----END CERTIFICATE-----\n" % (data)
  return data


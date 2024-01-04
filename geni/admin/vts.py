# Copyright (c) 2014-2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, print_function

import json

import requests

from . import germ

class Connection(germ.Connection):
  def __init__ (self):
    super(Connection, self).__init__()
    self.user = "foamadmin"

  @property
  def pgcmid (self):
    url = "%s/core/admin/vts/pg-cmid" % (self.baseurl)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]

  @pgcmid.setter
  def pgcmid (self, val):
    url = "https://%s:%d/core/admin/vts/pg-cmid/%s" % (self.host, self.port, val)
    requests.post(url, **self.rkwargs)

  @property
  def pgvlans (self):
    url = "https://%s:%d/core/admin/vts/pgvlans" % (self.host, self.port)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]

  @property
  def slivers (self):
    url = "https://%s:%d/core/admin/vts/slivers" % (self.host, self.port)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]

  @property
  def images (self):
    url = "https://%s:%d/core/admin/vts/images" % (self.host, self.port)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]

  @property
  def bridges (self):
    url = "https://%s:%d/core/admin/vts/ovs/bridges" % (self.host, self.port)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]

  def deleteSlivers (self, slice_urn):
    url = "%s/core/admin/vts/slice/%s" % (self.baseurl, slice_urn)
    r = requests.delete(url, **self.rkwargs)
    return r.json()["value"]

  def addTargetBridge (self, name, brname):
    url = "https://%s:%d/core/admin/vts/target-bridge" % (self.host, self.port)
    d = json.dumps({"name" : name, "brname" : brname})
    requests.post(url, d, **self.rkwargs)

  def addPGVlan (self, name, vid):
    url = "https://%s:%d/core/admin/vts/pgvlan" % (self.host, self.port)
    d = json.dumps({"name" : name, "vid" : vid})
    requests.post(url, d, **self.rkwargs)

  def setSSLVPNIP (self, ipstr):
    url = "https://%s:%d/core/admin/vts/vf/sslvpn/local-ip" % (self.host, self.port)
    d = json.dumps(ipstr)
    requests.post(url, d, **self.rkwargs)

  def addCircuitPlane (self, typ, label, endpoint, mtu, types = None, encoded = True):
    if not types: types = []

    url = "https://%s:%d/core/admin/vts/circuitplane/%s" % (self.host, self.port, typ)
    d = json.dumps({"label" : label, "endpoint" : endpoint,
                    "supported-types" : types, "encoded" : encoded, "mtu" : mtu})
    r = requests.put(url, d, **self.rkwargs)
    return r

  def removeCircuitPlane (self, label):
    url = "https://%s:%d/core/admin/vts/circuitplane/%s" % (self.host, self.port, label)
    requests.delete(url, **self.rkwargs)

  def getDatapaths (self, sliver_urn):
    url = "https://%s:%d/core/admin/vts/sliver/%s/datapaths" % (self.host, self.port, sliver_urn)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]

  def deleteDatapath (self, dpname, really = False):
    if not really:
      print("WARNING!!!!  You do not want to do this to datapaths managed by a sliver unless you really know what you are doing.")
      return
    url = "https://%s:%d/core/admin/vts/ovs/bridge/%s" % (self.host, self.port, dpname)
    r = requests.delete(url, **self.rkwargs)
    return r.json()["value"]

  def getContainers (self, sliver_urn):
    url = "https://%s:%d/core/admin/vts/sliver/%s/containers" % (self.host, self.port, sliver_urn)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]

  def getRequestRspec (self, sliver_urn):
    url = "https://%s:%d/core/admin/vts/sliver/%s/request-rspec" % (self.host, self.port, sliver_urn)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]

  def getManifestRspec (self, sliver_urn):
    url = "https://%s:%d/core/admin/vts/sliver/%s/manifest-rspec" % (self.host, self.port, sliver_urn)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]

  def removePort (self, sliver_urn, dpname, client_id):
    url = "https://%s:%d/core/admin/vts/sliver/%s/datapath/%s/port/%s" % (self.host, self.port,
                                                                          sliver_urn, dpname, client_id)
    r = requests.delete(url, **self.rkwargs)
    return r.json()["value"]

  def addPGLocal (self, sliver_urn, dpname, client_id, pgcircuit):
    url = "https://%s:%d/core/admin/vts/sliver/%s/datapath/%s/port/%s" % (self.host, self.port,
                                                                          sliver_urn, dpname, client_id)
    d = json.dumps({"type" : "pg-local", "shared-lan" : pgcircuit})
    r = requests.put(url, d, **self.rkwargs)
    return r.json()["value"]

  def addImage (self, image_name):
    url = "https://%s:%d/core/admin/vts/image" % (self.host, self.port)
    d = json.dumps({"name" : image_name})
    r = requests.post(url, d, **self.rkwargs)
    return r.json()["value"]

  def setURNLock (self, sliver_urn, user_urn):
    url = "https://%s:%d/core/admin/vts/sliver/%s/lock" % (self.host, self.port, sliver_urn)
    d = json.dumps({"user-urn" : user_urn})
    r = requests.put(url, d, **self.rkwargs)
    return r.json()["value"]

  def deleteDropboxVol (self, sliver_uuid):
    url = "https://%s:%d/core/admin/vts/dropbox/%s" % (self.host, self.port, sliver_uuid)
    r = requests.delete(url, **self.rkwargs)
    return r.json()["value"]

  def deallocateSliver (self, sliver_urn):
    url = "https://%s:%d/core/admin/vts/sliver/%s/deallocate" % (self.host, self.port, sliver_urn)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]

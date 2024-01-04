# Copyright (c) 2015  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import requests

import geni._coreutil as GCU

import requests.packages.urllib3
import requests.packages.urllib3.exceptions
requests.packages.urllib3.disable_warnings((requests.packages.urllib3.exceptions.InsecureRequestWarning,
                                            requests.packages.urllib3.exceptions.InsecurePlatformWarning))

class Link(object):
  def __init__ (self, item):
    self.rel = item["rel"]
    self.href = item["href"]
    self.type = item["type"]


class ResourceDiscovery(object):
  def __init__ (self, name, host, port = 443, url = None):
    self.name = name
    self.url = url
    if self.url is None:
      self.url = "https://%s:%d" % (host, port)

    self._uid = None
    self._version = None
    self._release = None
    self._links = {}

  def _populate (self):
    r = requests.get(self.url, **self.rkwargs)
    data = r.json()
    self._uid = data["uid"]
    self._version = data["version"]
    self._release = data["release"]
    for item in data["links"]:
      self._links[item["rel"]] = Link(item)

  @property
  def rkwargs (self):
    d = {"headers" : self.headers,
         "verify" : False}
    return d

  @property
  def headers (self):
    d = {"Content-Type" : "application/json"}
    d.update(GCU.defaultHeaders())
    return d

  @property
  def uid (self):
    if not self._uid:
      self._populate()
    return self._uid

  @property
  def version (self):
    if not self._version:
      self._populate()
    return self._version
    
  @property
  def release (self):
    if not self._release:
      self._populate()
    return self._release

  @property
  def sites (self):
    if not self._links:
      self._populate()
    shref = self._links["sites"].href
    r = requests.get("%s%s" % (self.url, shref), **self.rkwargs)
    data = r.json()
    for site in data["items"]:
      yield Site(site)


class Site(object):
  def __init__ (self, item):
    self._links = {}
    self.description = item["description"]
    self.name = item["name"]
    self.uid = item["uid"]
    self.location = item["location"]
    self.latitude = item["latitude"]
    self.longitude = item["longitude"]
    for ldata in item["links"]:
      self._links[ldata["rel"]] = Link(ldata)


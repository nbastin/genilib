# Copyright (c) 2014-2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json

import requests
import requests.auth

import requests.packages.urllib3
import requests.packages.urllib3.exceptions
requests.packages.urllib3.disable_warnings((requests.packages.urllib3.exceptions.InsecureRequestWarning,
                                            requests.packages.urllib3.exceptions.InsecurePlatformWarning))

class Connection(object):
  def __init__ (self):
    self.user = "germadmin"
    self.password = None
    self.host = "localhost"
    self.port = 3626

  @property
  def baseurl (self):
    return "https://%s:%d" % (self.host, self.port)

  @property
  def rkwargs (self):
    d = {"headers" : self.headers,
         "auth" : self.auth,
         "verify" : False}
    return d

  @property
  def headers (self):
    return {"Content-Type" : "application/json"}

  @property
  def auth (self):
    return requests.auth.HTTPBasicAuth(self.user, self.password)

  @property
  def configkeys (self):
    url = "%s/core/admin/get-config-keys" % (self.baseurl)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]

  @property
  def version (self):
    url = "%s/core/admin/get-version" % (self.baseurl)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]["version"]

  def getConfig (self, key):
    url = "%s/core/admin/get-config" % (self.baseurl)
    d = json.dumps({"key":key})
    r = requests.post(url, d, **self.rkwargs)
    return r.json()["value"]

  def setConfig (self, key, value):
    url = "%s/core/admin/set-config" % (self.baseurl)
    d = json.dumps({"key":key, "value":value})
    r = requests.post(url, d, **self.rkwargs)
    return r.json()["value"]

  def setLocation (self, country, latitude, longitude):
    url = "%s/core/admin/set-location" % (self.baseurl)
    d = json.dumps({"country" : country, "long" : longitude, "lat" : latitude})
    r = requests.post(url, d, **self.rkwargs)
    return r.json()["value"]

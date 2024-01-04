# Copyright (c) 2014-2015  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from __future__ import absolute_import

from . import RSpec

class Request(RSpec):
  def __init__ (self):
    super(Request, self).__init__("request")
    self._resources = []

  def addGroup (self, name):
    group = Group(name)
    self._resources.append(group)
    return group

  def buildMatch (self):
    match = Match()
    self._resources.append(match)
    return match

  @property
  def resources(self):
    return self._resources

class Datapath(object):
  def __init__ (self, ad_dp = None):
    self._ad_dp = ad_dp

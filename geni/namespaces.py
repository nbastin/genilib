# Copyright (c) 2013-2015  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class Namespace(object):
  def __init__ (self, prefix, name, location = None):
    self.prefix = prefix
    self.name = name
    self.location = location

  def __repr__ (self):
    return self.name

XSNS = Namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

REQUEST = Namespace("request", "http://www.geni.net/resources/rspec/3", "http://www.geni.net/resources/rspec/3/request.xsd")
OFv3 = Namespace("openflow", "http://www.geni.net/resources/rspec/ext/openflow/3")
OFv4 = Namespace("openflow", "http://www.geni.net/resources/rspec/ext/openflow/4")
SVLAN = Namespace("sharedvlan", "http://www.geni.net/resources/rspec/ext/shared-vlan/1",
                  "http://www.geni.net/resources/rspec/ext/shared-vlan/1/request.xsd")
OPSTATE = Namespace("opstate", "http://www.geni.net/resources/rspec/ext/opstate/1",
                    "http://http://www.geni.net/resources/rspec/ext/opstate/1/ad.xsd")
USER = Namespace("user", "http://www.geni.net/resources/rspec/ext/user/1")

# Copyright (c) 2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from geni.aggregate import FrameworkRegistry
from geni.aggregate.context import Context
from geni.aggregate.user import User

def buildContext ():
  portal = FrameworkRegistry.get("portal")()
  portal.cert = "/home/nbastin/.ssh/portal-nbastin.pem"
  portal.key = "/home/nbastin/.ssh/portal-nbastin.key"

  nbastin = User()
  nbastin.name = "nbastin"
  nbastin.urn = "urn:publicid:IDN+ch.geni.net+user+nickbas"
  nbastin.addKey("/home/nbastin/.ssh/geni_dsa.pub")

  context = Context()
  context.addUser(nbastin, default = True)
  context.cf = portal
  context.project = "bss-sw-test"

  return context

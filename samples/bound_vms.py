# Copyright (c) 2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import geni.rspec.pg as PG
import geni.aggregate.instageni as IG

import nbastin

context = nbastin.buildContext()

#IG.Utah.deletesliver(context, "xen-test2")

r = PG.Request()

for x in [1,2,3]:
  vm = PG.XenVM("xen%d" % (x))
  intf = vm.addInterface("if0")
  intf.component_id = "eth%d" % (x)
  r.addResource(vm)

  lnk = PG.Link()
  lnk.addInterface(intf)
  lnk.connectSharedVlan("mesoscale-openflow")
  r.addResource(lnk)

manifest = IG.Utah.createsliver(context, "xen-test2", r)
for node in manifest.nodes:
  for login in node.logins:
    print "[%s] %s:%d" % (node.name, login.hostname, login.port)


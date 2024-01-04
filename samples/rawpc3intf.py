# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import itertools

import example_config
import geni.rspec.pg as PG
import geni.aggregate.instageni as IG

context = example_config.buildContext()

ad = IG.NYSERNet.listresources(context)

pairs = itertools.izip(xrange(1,4), [x.name for x in ad.shared_vlans if x.name.startswith("vts")])

r = PG.Request()

pc = PG.RawPC("bss-rtr")
pc.routeable_control_ip = True
for (i,vlan) in pairs:
  intf = pc.addInterface("if%d" % (i))
  intf.component_id = "eth%d" % (i)

  lnk = PG.Link()
  lnk.addInterface(intf)
  lnk.connectSharedVlan(vlan)
  r.addResource(lnk)

  vm = PG.XenVM("xen-%d" % (i))
  intf = vm.addInterface("if0")
  lnk = PG.Link()
  lnk.addInterface(intf)
  lnk.connectSharedVlan(vlan)
  r.addResource(vm)
  r.addResource(lnk)

r.addResource(pc)

manifest = IG.NYSERNet.createsliver(context, "xen-test2", r)

# Copyright (c) 2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import geni.aggregate.instageni as IG
import geni.rspec.pg as PG
import nbastin
import itertools

context = nbastin.buildContext()

ad = IG.Illinois.listresources(context)
vtsvlans = []
for vlan in ad.shared_vlans:
  if vlan.name.startswith("vts"):
    vtsvlans.append(vlan.name)

r = PG.Request()

node = PG.RawPC("geevts0")
node.disk_image = "urn:publicid:IDN+utahddc.geniracks.net+image+emulab-ops:FEDORA15-STD"

intfs = []
for idx in xrange(1,4):
  intf = node.addInterface("if%d" % (idx))
  intf.component_id = "eth%d" % (idx)
  intfs.append(intf)
  lnk = PG.Link()
  lnk.addInterface(intf)
  lnk.connectSharedVlan("mesoscale-openflow")
  r.addResource(lnk)

pairs = zip(itertools.cycle(intfs), vtsvlans)
for (intf, vlan) in pairs:
  lnk = PG.Link()
  lnk.addInterface(intf)
  lnk.connectSharedVlan(vlan)
  r.addResource(lnk)

r.addResource(node)

r.write("geevts.xml")




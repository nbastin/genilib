# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import itertools

import nbastin
import geni.aggregate.instageni
import geni.rspec.pg as PG

context = nbastin.buildContext()
am = geni.aggregate.instageni.UtahDDC

#am.deletesliver(context, "vts-stage")
ad = am.listresources(context)

vtsvlans = []
for vlan in ad.shared_vlans:
  if vlan.name.startswith("vts"):
    vtsvlans.append(vlan.name)

r = PG.Request()

node = PG.RawPC("vts")
node.disk_image = "https://www.instageni.maxgigapop.net/image_metadata.php?uuid=3219aad0-ac89-11e3-b767-000000000000"

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

mfest = am.createsliver(context, "vts-stage", r)
print mfest.text
print mfest

# Copyright (c) 2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import geni.rspec.pg as PG
import geni.rspec.pgad
import geni.aggregate.instageni as IG
import nbastin

DISK_IMAGE = "urn:publicid:IDN+instageni.gpolab.bbn.com+image+emulab-ops:UBUNTU12-64-STD"

context = nbastin.buildContext()

xenshared = []
ad = IG.UtahDDC.listresources(context)
for node in ad.nodes:
  if node.available and node.shared:
    if "emulab-xen" in node.sliver_types:
      xenshared.append(node)

r = PG.Request()

n1 = PG.XenVM("xen1", component_id = xenshared[0].component_id)
n1.disk_image = DISK_IMAGE

n2 = PG.XenVM("xen2", component_id = xenshared[1].component_id)
n2.disk_image = DISK_IMAGE

r.addResource(n1)
r.addResource(n2)

for lan in xrange(0, 45):
  i1 = n1.addInterface("if%d" % (lan))
  i2 = n2.addInterface("if%d" % (lan))
  i1.bandwidth = 10000
  i2.bandwidth = 10000
  lnk = PG.LAN("lan-%d" % (lan))
  lnk.addInterface(i1)
  lnk.addInterface(i2)
  r.addResource(lnk)

r.write("pwe-build.xml")

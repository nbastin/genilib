# Copyright (c) 2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import itertools

import example_config

import geni.aggregate.instageni
import geni.rspec.pg as PG

context = example_config.buildContext()

am = geni.aggregate.instageni.GPO
ad = am.listresources(context)

vtslans = []

for vlan in ad.shared_vlans:
  if vlan.name.startswith("vts"):
    vtslans.append(vlan.name)

r = PG.Request()

node = PG.RawPC("vts")

intfs = []
for idx in xrange(1,4):
  # Make interfaces attached to specific pnics, attach them all to mesoscale vlan
  intf = node.addInterface("if%d" % (idx))
  intf.component_id = "eth%d" % (idx)
  intfs.append(intf)
  lnk = PG.Link()
  lnk.addInterface(intf)
  lnk.connectSharedVlan("mesoscale-openflow")
  r.addResource(lnk)

# Evenly spread all the shared VLANs we found over the pnics
pairs = zip(itertools.cycle(intfs), vtslans)
for (intf, vlan) in pairs:
  lnk = PG.Link()
  lnk.addInterface(intf)
  lnk.connectSharedVlan(vlan)
  r.addResource(lnk)
  
r.addResource(node)

r.write("gpo-pwe.xml")
 
#am.createsliver(context, "pw-beta", r)

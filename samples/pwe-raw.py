# Copyright (c) 2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import geni.rspec.pg as PG

DISK_IMAGE = "https://www.emulab.net/image_metadata.php?uuid=653fdd27-5cb3-11e3-83eb-001143e453fe"

def bindVlans(rspec, pc, cid, start, end):
  for vlan in xrange(start,end+1):
    intf = pc.addInterface("if%d" % (vlan))
    intf.component_id = cid
    lnk = PG.Link()
    lnk.addInterface(intf)
    lnk.connectSharedVlan("pwe-segment-%d" % (vlan))
    rspec.addResource(lnk)
    
  intf = pc.addInterface("meso:%s" % (cid))
  intf.component_id = cid
  lnk = PG.Link()
  lnk.addInterface(intf)
  lnk.connectSharedVlan("mesoscale-openflow")
  rspec.addResource(lnk)


r = PG.Request()

pc = PG.RawPC("pwe-router")
pc.disk_image = DISK_IMAGE

r.addResource(pc)

bindVlans(r, pc, "eth1", 1, 10)
bindVlans(r, pc, "eth2", 11, 20)
bindVlans(r, pc, "eth3", 21, 30)

r.write("pwe-raw.xml")

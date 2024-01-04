# Copyright (c) 2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import geni.rspec.pg as PG

DISK_IMAGE = "https://www.emulab.net/image_metadata.php?uuid=653fdd27-5cb3-11e3-83eb-001143e453fe"

r = PG.Request()

pc = PG.RawPC("pwe-router")
pc.disk_image = DISK_IMAGE

r.addResource(pc)

for (num, cid) in [(301, "eth1"), (302, "eth2"), (303, "eth3")]:
  intf = pc.addInterface("if%d" % (num))
  intf.component_id = cid
  lnk = PG.Link()
  lnk.addInterface(intf)
  lnk.connectSharedVlan("vts%d" % (num))
  r.addResource(lnk)

r.write("pwe-bbn-test.xml")

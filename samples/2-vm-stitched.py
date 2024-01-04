# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import geni.rspec.pg as PG
import geni.aggregate.instageni as IG

SITES = [IG.UtahDDC, IG.GPO]

###
# Request a Xen VM at two IG sites and build a stitched link between them
###

r = PG.Request()

intfs = []
for idx,site in enumerate(SITES):
  vm = PG.XenVM("vm%d" % (idx))
  vm.component_manager_id = site.component_manager_id
  intfs.append(vm.addInterface("if0"))
  r.addResource(vm)

lnk = PG.StitchedLink()
for intf in intfs:
  lnk.addInterface(intf)
r.addResource(lnk)

r.write("stitched.xml")

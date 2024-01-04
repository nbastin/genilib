# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import geni.rspec.pg as PG
import geni.rspec.igext as IGX
#import geni.aggregate.instageni as IG
#import geni.aggregate.apis

#import nbastin

#context = nbastin.buildContext()
#context.debug = True

#try:
#  IG.GPO.deletesliver(context, "xen-test2")
#except geni.aggregate.apis.AMError, e:
#  pass

r = PG.Request()

vm1 = IGX.XenVM("xen1")
intf1 = vm1.addInterface("if0")
r.addResource(vm1)

vm2 = IGX.XenVM("xen2")
intf2 = vm2.addInterface("if0")
r.addResource(vm2)

lnk = PG.Link()
lnk.addInterface(intf1)
lnk.addInterface(intf2)
lnk.bandwidth = 1000000
lnk.disableMACLearning()

r.addResource(lnk)

r.writeXML("dac.xml")

#manifest = IG.GPO.createsliver(context, "xen-test2", r)
#print manifest.text

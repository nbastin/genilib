# Copyright (c) 2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import geni.rspec.vts as VTS
import geni.rspec.pg as PG
import geni.aggregate.vts as VTSAM
import geni.aggregate.instageni as IG
import geni.util

import nbastin
context = nbastin.buildContext()

SLICE = "gec-20-demo"

geni.util.deleteSliverExists(VTSAM.DDC, context, SLICE)


# VTS Request

image = VTS.OVSL2Image()

r = VTS.Request()
vpnf = VTS.SSLVPNFunction("vpn-1")
dp = VTS.Datapath(image, "dp-ddc")
dp.attachPort(VTS.VFCircuit("vpn-1"))
dp.attachPort(VTS.PGCircuit())

r.addResource(dp)
r.addResource(vpnf)

r.write("ddc-vts-request.xml")

manifest = VTSAM.DDC.createsliver(context, SLICE, r)
manifest.write("ddc-vts-manifest.xml")

#r = PG.Request()
#vm = PG.XenVM("vm0")
#intf = vm.addInterface("if0")
#r.addResource(vm)
#
#lnk = PG.Link()
#lnk.addInterface(intf)
#lnk.connectSharedVlan("vts-3622")
#r.addResource(lnk)
#
#r.write("ddc-pg-request.xml")
#m = IG.UtahDDC.createsliver(context, SLICE, r)
#m.write("ddc-pg-manifest.xml")

# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import geni.rspec.pg as PG
import geni.aggregate.instageni as IG

import nbastin
context = nbastin.buildContext()

NETMASK = "255.255.255.0"
HOST_IPS = ["10.10.1.1", "10.10.1.2", "10.10.1.3"]
OVS_IPS = ["10.10.1.11", "10.10.1.12", "10.10.1.13"]
BLACKLIST = set([IG.UtahDDC, IG.NPS])

for site in IG.aggregates():
  print site.name
  if site in BLACKLIST:
    continue

  try:
    ad = site.listresources(context)
  except Exception:
    # Continue past aggregates that are down
    continue

  cmid = ad.nodes[0].component_manager_id

  r = PG.Request()
  ovs_intfs = []

  ovs = PG.XenVM("OVS")
  ovs.disk_image = "urn:publicid:IDN+utahddc.geniracks.net+image+emulab-ops:Ubuntu12-64-OVS"
  ovs.addService(PG.Execute(shell="sh", command = "sudo /local/install-script.sh"))
  ovs.addService(PG.Install(path="/local", url = "http://www.gpolab.bbn.com/experiment-support/OpenFlowOVS/of-ovs.tar.gz"))
  ovs.component_manager_id = cmid
  for idx in xrange(0,3):
    intf = ovs.addInterface("if%d" % (idx))
    intf.addAddress(PG.IPv4Address(OVS_IPS[idx], NETMASK))
    ovs_intfs.append(intf)
  r.addResource(ovs)

  for ct in xrange(0,3):
    vzc = PG.VZContainer("host%d" % (ct+1))
    vzc.component_manager_id = cmid
    intf = vzc.addInterface("if0")
    intf.addAddress(PG.IPv4Address(HOST_IPS[ct], NETMASK))
    r.addResource(vzc)
    link = PG.LAN()
    link.addInterface(intf)
    link.addInterface(ovs_intfs[ct])
    link.enableVlanTagging()
    r.addResource(link)

  r.write("ovs-%s.rspec" % (site.name))

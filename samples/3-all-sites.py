# Copyright (c) 2016-2017  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import geni.rspec.pg as PG
import geni.aggregate.instageni as IG

import nbastin
context = nbastin.buildContext()

NETMASK = "255.255.255.0"
IPS = ["10.10.1.1", "10.10.1.2", "10.10.1.3"]
BLACKLIST = set([IG.UtahDDC, IG.NPS])

for site in IG.aggregates():
  print "Running for %s" % (site.name)

  if site in BLACKLIST:
    continue

  try:
    ad = site.listresources(context)
  except Exception:
    # Continue past aggregates that are down
    continue

  r = PG.Request()
  intfs = []

  # Xen VMs
  for (idx, node) in enumerate([node for node in ad.nodes if not node.exclusive and "emulab-xen" in node.sliver_types]):
    vm = PG.XenVM("host%d" % (idx+1))
    intf = vm.addInterface("if0")
    intf.addAddress(PG.IPv4Address(IPS[idx], NETMASK))
    r.addResource(vm)
    intfs.append(intf)
    vm.component_id = node.component_id
    vm.component_manager_id = node.component_manager_id

  # VZNode
  # Sorry about the stupidity about how to find OpenVZ hosts.  I should fix this.
  vznode = [node for node in ad.nodes if not node.exclusive and "emulab-xen" not in node.sliver_types and "pcvm" in node.hardware_types][0]
  vzc = PG.VZContainer("host3")
  intf = vzc.addInterface("if0")
  intf.addAddress(PG.IPv4Address(IPS[2], NETMASK))
  r.addResource(vzc)
  intfs.append(intf)
  vzc.component_id = vznode.component_id
  vzc.component_manager_id = vznode.component_manager_id

  # Controller
  cvm = PG.XenVM("controller")
  cvm.routable_control_ip = True
  cvm.component_manager_id = vznode.component_manager_id
  cvm.addService(PG.Install(url="http://www.gpolab.bbn.com/experiment-support/OpenFlowHW/of-hw.tar.gz", path="/local"))
  cvm.addService(PG.Execute(shell="sh", command = "sudo /local/install-script.sh"))
  r.addResource(cvm)

  # Big LAN!
  lan = PG.LAN()
  for intf in intfs:
    lan.addInterface(intf)
  lan.connectSharedVlan("mesoscale-openflow")
  r.addResource(lan)

  r.write("%s.rspec" % (site.name))

# Copyright (c) 2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import geni.rspec.pg as PG

DISK_IMAGE = "urn:publicid:IDN+instageni.gpolab.bbn.com+image+emulab-ops:UBUNTU12-64-STD"
ndata = [("bbn-ig-ps103-a", "10.42.103.111"), ("bbn-ig-ps103-b", "10.42.103.112")]

r = PG.Request()

for (name, ip) in ndata:
  vm = PG.XenVM(name)
  vm.disk_image = DISK_IMAGE
  vm.addService(PG.Install(url="http://www.gpolab.bbn.com/~jbs/dingbot-jbs.tar.gz", path="/opt"))
  vm.addService(PG.Install(url="http://www.gpolab.bbn.com/~jbs/dingbot.tar.gz", path="/opt"))
  vm.addService(PG.Execute(shell="/bin/bash", command="sudo /opt/dingbot/dingbot /opt/dingbot/dingbot-jbs.json %s" % (vm.name)))
  intf = vm.addInterface("if0")
  intf.addAddress(PG.IPv4Address(ip, "255.255.255.0"))
  lnk = PG.Link()
  lnk.addInterface(intf)
  lnk.connectSharedVlan("mesoscale-openflow")
  r.addResource(vm)
  r.addResource(lnk)

r.write("ps103.xml")

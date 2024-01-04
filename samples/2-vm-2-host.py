# Copyright (c) 2014-2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import geni.rspec.pg as PG
import geni.aggregate.instageni as IG
import geni.rspec.igutil as IGU
import geni.rspec.igext as IGX
from geni import util


def main (sname, site, of_vlan = False, of_controller = None):
  # Load GENI credentials
  context = util.loadContext(key_passphrase = True)

  # Make a basic request with two VMs
  r = PG.Request()
  vms = []

  for idx in range(0,2):
    vm = r.XenVM("vm%d" % (idx))
    vm.addInterface("if0")
    vms.append(vm)

  lnk = r.Link()
  lnk.addInterface(vms[0].interfaces[0])
  lnk.addInterface(vms[1].interfaces[0])
  # Openflow-enable this link if requested
  if of_vlan:
    lnk.addChild(IGX.OFController(of_controller[0], of_controller[1]))
    
  # Find nodes that support VMs at the requested site
  ad = site.listresources(context)
  vmnodes = []
  for node in ad.nodes:
    if IGU.shared_xen(node):
      vmnodes.append(node)

  # Bind request VMs to different nodes by component_id
  for (vm, node) in zip(vms, vmnodes):
    vm.component_id = node.component_id

  # Save the request
  r.writeXML("%s-%s-request.xml" % (sname, site.name))

  # Make the reservation
  m = site.createsliver(context, sname, r)

  # Save the manifest
  m.writeXML("%s-%s-manifest.xml" % (sname, site.name))

  # Output login info to stdout
  util.printlogininfo(manifest = m)


if __name__ == '__main__':
  ### Non-OF, will be restricted to 100Mbits/sec due to PG shaping
  #main("test-2", IG.Stanford)

  ### Private-OF
  #main("test-1", IG.Stanford, True, ("54.209.87.26", 7733))
  pass

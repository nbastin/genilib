#!/usr/bin/env python

import geni.portal as portal
import geni.rspec.pg as RSpec
import geni.rspec.igext as IG

nodeset = {
    'n1' : { 'bandwidth' : 100000, 'latency' : 0,  'plr' : 0.0  }, 
    'n2' : { 'bandwidth' : 50000,  'latency' : 5,  'plr' : 0.05 }, 
    'n3' : { 'bandwidth' : 25000,  'latency' : 10, 'plr' : 0.02 }, 
    'n4' : { 'bandwidth' : 10000,  'latency' : 20, 'plr' : 0.0  },
}

rspec = RSpec.Request()

tour = IG.Tour()
tour.Description(IG.Tour.TEXT,
                 "Four PCs with individual shaping parameters on the same LAN.")
tour.Instructions(IG.Tour.MARKDOWN,
                  "None")
rspec.addTour(tour)

pc = portal.Context()

lan = RSpec.LAN("shaped-lan")
rspec.addResource(lan)

for nid,sparms in nodeset.items():
    node = RSpec.RawPC(nid)
    rspec.addResource(node)
    iface = node.addInterface("if1")
    for parm,val in sparms.items():
        iface.__dict__[parm] = val
    lan.addInterface(iface)

pc.printRequestRSpec(rspec)

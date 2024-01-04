#!/usr/bin/env python

import geni.portal as portal
import geni.rspec.pg as RSpec
import geni.rspec.igext as IG

rspec = RSpec.Request()

tour = IG.Tour()
tour.Description(IG.Tour.TEXT,
                 "Two PCs connected via a link with asymmetric shaping for each.")
tour.Instructions(IG.Tour.MARKDOWN,
                  "None")
rspec.addTour(tour)

pc = portal.Context()

link = RSpec.LAN("shaped-link")
rspec.addResource(link)

node1 = RSpec.RawPC("node-1")
rspec.addResource(node1)
iface1 = node1.addInterface("if1")
iface1.bandwidth = 50000
iface1.latency = 5
iface1.plr = 0.05
link.addInterface(iface1)

node2 = RSpec.RawPC("node-2")
rspec.addResource(node2)
iface2 = node2.addInterface("if2")
iface2.bandwidth = 20000
iface2.latency = 15
iface2.plr = 0.1
link.addInterface(iface2)

pc.printRequestRSpec(rspec)

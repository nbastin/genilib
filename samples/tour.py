#!/usr/bin/env python

import geni.rspec.pg as rspec
import geni.rspec.igext as ig
import geni.portal as portal

pc = portal.Context()
rspec = pc.makeRequestRSpec()

tour = ig.Tour()
tour.Description(ig.Tour.TEXT,"Test description")
tour.Instructions(ig.Tour.TEXT,"Text instructions")

node1 = rspec.XenVM("src")
node2 = rspec.XenVM("dst")
link1 = rspec.Link("thelink", members = [node1, node2])

tour.addStep(ig.Tour.Step(node1,"This is the first node"))
tour.steps.append(ig.Tour.Step(node2,"This is the second node"))
tour.steps.append(ig.Tour.Step(link1,"This is the link"))

rspec.addTour(tour)
pc.printRequestRSpec()

#!/usr/bin/env python

import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.igext as IG
import geni.rspec.emulab as emulab

from lxml import etree as ET

pc = portal.Context()
request = rspec.Request()

pc.defineParameter("param1", "dsc1", portal.ParameterType.INTEGER, 1)
pc.defineParameter("param2", "dsc2", portal.ParameterType.STRING, "value2")

params = pc.bindParameters()

ele2 = ET.Element("xmlstuff")
ET.SubElement(ele2, "evenmorexml")

node1 = IG.XenVM("node1")
iface1 = node1.addInterface("if1")

# Add user data to node1 in a single line
node1.UserData(emulab.UserDataSet({"data1":ele2, "data2":"val2"}))


link = rspec.Link("link")
link.addInterface(iface1)

# Add user data to link over several lines
linkdata = emulab.UserDataSet()
linkdata.addData("linkdata1", "val1")
linkdata.addData("linkdata2", "val2")
link.UserData(linkdata)

request.addResource(node1)
request.addResource(link)
pc.verifyParameters()
pc.printRequestRSpec(request)

"""
This is an example intended for use the the CloudLab / Apt portal. It allows
the user to select the hardware type, number of nodes, and toggle whether or
not they go into a LAN.

Instructions:

Just use as you would use any other slice
"""

import geni.portal as portal
import geni.rspec.pg as RSpec

hw_types = [("m400", "ARM64"), ("dl360", "x86-64")]

pc = portal.Context()

pc.defineParameter("N", "Number of nodes",
                   portal.ParameterType.INTEGER, 5)
pc.defineParameter("hwtype", "Hardware type",
                   portal.ParameterType.NODETYPE, "m400", hw_types)
pc.defineParameter("lan",  "Put all nodes in a LAN",
                   portal.ParameterType.BOOLEAN, False)

params = pc.bindParameters()

rspec = RSpec.Request()

if (params.lan):
    lan = RSpec.LAN()
    rspec.addResource(lan)

for i in range(1, params.N+1):
  node = RSpec.RawPC("node%d" % i)
  node.hardware_type = params.hwtype
  rspec.addResource(node)

  if params.lan:
    iface = node.addInterface("eth0")
    lan.addInterface(iface)

pc.printRequestRSpec(rspec)

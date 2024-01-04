"""This profile demonstrates the use of the BridgedLink class, which
is syntactic sugar for creating two links separated by an Emulab
bridge (delay) node. The BridgedLink class will create the following
topology:

	      left-link          right-link
	node1 =========== bridge ============ node2

The _bridge_ is a special node type (sliver_type="delay") that tells the CM
to insert an Emulab delay node instead of a plain (router) node. A delay
node is a transparent Ethernet bridge between the left and right segments
above, but on which the traffic can be shaped wrt. bandwidth, latency, and
loss.

Instructions:
Log into the bridge node and do:
```
	sudo ifconfig bridge1
```
this will tell you what interfaces are attached to the bridge. Do this to
see the current shaping parameters on the bridge:
```
	sudo ipfw pipe show
```
For more info, do a man on ipfw and look for the section on dummynet.

To test the bridge, log into node1 and `ping node2`."""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the emulab extensions library.
import geni.rspec.emulab as emulab

# Create a portal context.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Add a raw PC to the request and give it an interface.
node1 = request.RawPC("node1")
iface1 = node1.addInterface()
# Specify the IPv4 address
iface1.addAddress(pg.IPv4Address("192.168.1.1", "255.255.255.0"))

# Add another raw PC to the request and give it an interface.
node2 = request.RawPC("node2")
iface2 = node2.addInterface()
# Specify the IPv4 address
iface2.addAddress(pg.IPv4Address("192.168.1.2", "255.255.255.0"))

# Create the bridged link between the two nodes.
link = request.BridgedLink("link")
# Add the interfaces we created above.
link.addInterface(iface1)
link.addInterface(iface2)

# Give bridge some shaping parameters.
link.bandwidth = 10000
link.latency   = 15

# Done
pc.printRequestRSpec(request)

